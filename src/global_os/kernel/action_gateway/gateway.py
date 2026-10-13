"""Tool Gateway — verifies proposal-bound ExecutionToken; reconciles world effects."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from global_os.common.hashing import content_hash, new_id
from global_os.contracts.validate import validate
from global_os.kernel.authority.approvals import (
    ApprovalInvalid,
    ApprovalService,
    ApprovalToken,
)
from global_os.kernel.authority.execution_token import (
    ExecutionTokenClaims,
    ExecutionTokenError,
    ExecutionTokenService,
)
from global_os.kernel.policy.confirm import (
    ConfirmationPolicy,
    ConfirmationRequired,
    RiskAssessment,
    enforce_confirmation,
)
from global_os.runtime.events.ledger import EventLedger


class ToolGatewayError(Exception):
    pass


class MissingExecutionToken(ToolGatewayError):
    pass


class CapabilityToolMismatch(ToolGatewayError):
    """Token/proposal capability does not satisfy tool required_capabilities (GOS-I03)."""


class DeniedActionReachedGateway(ToolGatewayError):
    """Raised when a DENY path somehow reaches the gateway — invariant break."""


class LegacyExecutionTokenForbidden(ToolGatewayError):
    """Raised when opaque accept_token path is used under production profile."""


class EffectReconciliationStatus(str, Enum):
    EXECUTED = "EXECUTED"
    OBSERVATION_PENDING = "OBSERVATION_PENDING"
    RECONCILED = "RECONCILED"
    DISCREPANCY = "DISCREPANCY"
    ESCALATION_REQUIRED = "ESCALATION_REQUIRED"
    COMPENSATION_REQUIRED = "COMPENSATION_REQUIRED"


@dataclass
class ToolResult:
    success: bool
    payload: dict[str, Any]


ToolHandler = Callable[[dict[str, Any]], ToolResult]


def reconcile_effect(
    *,
    tool_success: bool,
    intended_effect: str,
    observation: dict[str, Any] | None,
) -> tuple[EffectReconciliationStatus, str, str]:
    """ToolSuccess ≠ WorldSuccess (GOS-I13). Returns status, observed_effect, discrepancy."""
    del tool_success  # success alone never implies world success
    if observation is None:
        return (
            EffectReconciliationStatus.OBSERVATION_PENDING,
            "unobserved",
            "observation_pending",
        )
    observed = str(observation.get("effect", "unobserved"))
    if observed == intended_effect:
        return EffectReconciliationStatus.RECONCILED, observed, "none"
    discrepancy = f"expected={intended_effect} got={observed}"
    return EffectReconciliationStatus.DISCREPANCY, observed, discrepancy


def _extract_approval_token(proposal: dict[str, Any]) -> ApprovalToken | None:
    raw = proposal.get("approval_token")
    if isinstance(raw, ApprovalToken):
        return raw
    if isinstance(raw, dict) and "signature" in raw and "approval_id" in raw:
        return ApprovalToken(
            approval_id=str(raw["approval_id"]),
            approver=str(raw["approver"]),
            action_hash=str(raw["action_hash"]),
            goal_id=str(raw["goal_id"]),
            limits=dict(raw.get("limits") or {}),
            valid_until=str(raw["valid_until"]),
            one_time=bool(raw.get("one_time", True)),
            signature=str(raw["signature"]),
        )
    return None


class ToolGateway:
    def __init__(
        self,
        ledger: EventLedger,
        token_service: ExecutionTokenService | None = None,
        *,
        confirmation_policy: ConfirmationPolicy = ConfirmationPolicy.NEVER,
        allow_legacy_tokens: bool = False,
        approval_service: ApprovalService | None = None,
    ) -> None:
        self._ledger = ledger
        self._token_service = token_service or ExecutionTokenService()
        self._tools: dict[str, ToolHandler] = {}
        self._tool_caps: dict[str, tuple[str, ...]] = {}
        self._idempotency: dict[str, dict[str, Any]] = {}
        # Legacy deposit set — transitional only; prefer mint via ExecutionTokenService.
        # AUTH-001b: default DENY. Opt in explicitly for tests/dev harnesses only.
        self._legacy_tokens: set[str] = set()
        self._allow_legacy_tokens = allow_legacy_tokens
        self._confirmation_policy = confirmation_policy
        self._approval_service = approval_service

    def register_tool(
        self,
        tool_id: str,
        handler: ToolHandler,
        *,
        required_capabilities: Sequence[str] | None = None,
        spec: Any | None = None,
    ) -> None:
        """Register handler. Caps from ToolSpec-like ``spec`` or required_capabilities (GOS-I03)."""
        if spec is not None:
            caps = tuple(spec.required_capabilities)
            spec_id = str(spec.tool_id)
            if tool_id != spec_id:
                raise ToolGatewayError(
                    f"register tool_id={tool_id!r} != spec.tool_id={spec_id!r}"
                )
        elif required_capabilities is not None:
            caps = tuple(required_capabilities)
        else:
            raise ToolGatewayError(
                f"tool {tool_id!r} registered without required_capabilities/spec (GOS-I03)"
            )
        if not caps:
            raise ToolGatewayError(f"tool {tool_id!r} has empty required_capabilities")
        self._tools[tool_id] = handler
        self._tool_caps[tool_id] = caps

    def accept_token(self, token: str) -> None:
        """DEPRECATED: deposit opaque string. Prefer proposal-bound ExecutionToken mint."""
        if not self._allow_legacy_tokens:
            raise LegacyExecutionTokenForbidden(
                "legacy accept_token forbidden by default (AUTH-001b); "
                "pass allow_legacy_tokens=True only in tests/dev, or mint "
                "proposal-bound ExecutionToken"
            )
        self._legacy_tokens.add(token)

    def _approval_verified(self, proposal: dict[str, Any]) -> bool:
        """Bare approval_present bool is never trusted — only verified ApprovalToken."""
        token = _extract_approval_token(proposal)
        if token is None or self._approval_service is None:
            return False
        action_hash = content_hash({k: v for k, v in proposal.items() if k != "approval_token"})
        try:
            self._approval_service.verify_and_consume(
                token,
                action_hash=action_hash,
                goal_id=str(proposal.get("goal_id") or ""),
            )
        except ApprovalInvalid:
            return False
        return True

    def _enforce_capability_for_tool(
        self,
        *,
        tool_id: str,
        capability: str,
    ) -> None:
        required = self._tool_caps.get(tool_id)
        if required is None:
            raise ToolGatewayError(f"unknown tool: {tool_id}")
        if capability not in required:
            raise CapabilityToolMismatch(
                f"capability {capability!r} not in tool {tool_id!r} "
                f"required_capabilities={list(required)} (GOS-I03)"
            )

    def execute(
        self,
        *,
        tool_id: str,
        proposal: dict[str, Any],
        execution_token: str | None,
        tenant_id: str,
        workspace_id: str,
        intended_effect: str,
        observation: dict[str, Any] | None = None,
        require_observation: bool = False,
        material: bool = False,
        approval_present: bool = False,
        confirmation_policy: ConfirmationPolicy | None = None,
    ) -> dict[str, Any]:
        del approval_present  # never trusted; verified ApprovalToken only
        if not execution_token:
            raise MissingExecutionToken("Tool Gateway requires execution token (GOS-I03)")

        # Confirm gate: assessment ≠ enforcement; LLM security_risk ignored.
        policy = confirmation_policy or self._confirmation_policy
        risk: RiskAssessment | None = None
        try:
            bound = {**proposal, "tool_id": tool_id}
            risk = enforce_confirmation(
                bound, policy, approval_present=self._approval_verified(proposal)
            )
        except ConfirmationRequired:
            self._ledger.append(
                event_type="action.confirmation_required",
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                goal_id=proposal.get("goal_id"),
                principal_id=proposal.get("principal_id"),
                payload={
                    "tool_id": tool_id,
                    "policy": policy.value,
                },
                producer="kernel.action_gateway",
            )
            raise

        token_refs: dict[str, str]
        claims: ExecutionTokenClaims | None = None
        try:
            claims = self._token_service.verify_and_consume(execution_token, proposal=proposal)
            token_refs = {
                "execution_token_id": claims.token_id,
                "execution_token_jti_hash": content_hash(claims.jti),
                "execution_token_hash": content_hash(
                    {"token_id": claims.token_id, "jti": claims.jti}
                ),
            }
        except ExecutionTokenError:
            # AUTH-001b: legacy deposit only when explicitly opted in AND deposited.
            # Invalid/unbound/replayed proposal-bound tokens stay MissingExecutionToken.
            if self._allow_legacy_tokens and execution_token in self._legacy_tokens:
                self._legacy_tokens.discard(execution_token)
                token_refs = {
                    "execution_token_id": "legacy",
                    "execution_token_hash": content_hash(execution_token),
                }
            else:
                raise MissingExecutionToken(
                    "invalid, unbound, or already consumed execution token"
                ) from None

        capability = claims.capability if claims is not None else str(proposal.get("capability") or "")
        self._enforce_capability_for_tool(tool_id=tool_id, capability=capability)

        idem = proposal["idempotency_key"]
        if idem in self._idempotency:
            return self._idempotency[idem]

        handler = self._tools.get(tool_id)
        if handler is None:
            raise ToolGatewayError(f"unknown tool: {tool_id}")

        result = handler(proposal)
        if risk is not None:
            token_refs = {**token_refs, "risk": risk.risk.value, "risk_source": risk.source}
        action_id = new_id("act")
        self._ledger.append(
            event_type="action.executed",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=proposal.get("goal_id"),
            principal_id=proposal.get("principal_id"),
            payload={
                "action_id": action_id,
                "tool_id": tool_id,
                "success": result.success,
                "idempotency_key": idem,
                "reconciliation_status": EffectReconciliationStatus.EXECUTED.value,
                **token_refs,
            },
            producer="kernel.action_gateway",
        )

        recon_status, observed, discrepancy = reconcile_effect(
            tool_success=result.success,
            intended_effect=intended_effect,
            observation=observation,
        )
        if (material or require_observation) and observation is None:
            recon_status = EffectReconciliationStatus.OBSERVATION_PENDING
        if recon_status == EffectReconciliationStatus.DISCREPANCY and material:
            recon_status = EffectReconciliationStatus.ESCALATION_REQUIRED

        world_success = recon_status == EffectReconciliationStatus.RECONCILED

        receipt = {
            "receipt_id": new_id("er"),
            "schema_version": "0.1.0",
            "action_id": action_id,
            "tool_response": {"success": result.success},
            "intended_effect": intended_effect,
            "observed_effect": observed,
            "discrepancy": discrepancy,
            "verified_at": datetime.now(UTC).isoformat(),
            "verification_method": "observation_method" if observation else "tool_response_only",
            "reconciliation_status": recon_status.value,
            "world_success": world_success,
        }
        validate(receipt, "effect_receipt.schema.json")
        self._ledger.append(
            event_type="effect.receipted",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=proposal.get("goal_id"),
            principal_id=proposal.get("principal_id"),
            payload=receipt,
            producer="kernel.action_gateway",
        )
        if recon_status in {
            EffectReconciliationStatus.DISCREPANCY,
            EffectReconciliationStatus.ESCALATION_REQUIRED,
            EffectReconciliationStatus.COMPENSATION_REQUIRED,
        }:
            self._ledger.append(
                event_type="effect.discrepancy",
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                goal_id=proposal.get("goal_id"),
                principal_id=proposal.get("principal_id"),
                payload={
                    "action_id": action_id,
                    "reconciliation_status": recon_status.value,
                    "discrepancy": discrepancy,
                    "tool_success": result.success,
                    "world_success": False,
                },
                producer="kernel.action_gateway",
            )
        self._idempotency[idem] = receipt
        return receipt
