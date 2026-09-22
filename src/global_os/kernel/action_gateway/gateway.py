"""Tool Gateway — verifies proposal-bound ExecutionToken; reconciles world effects."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from global_os.common.hashing import content_hash, new_id
from global_os.contracts.validate import validate
from global_os.kernel.authority.execution_token import (
    ExecutionTokenError,
    ExecutionTokenService,
)
from global_os.runtime.events.ledger import EventLedger


class ToolGatewayError(Exception):
    pass


class MissingExecutionToken(ToolGatewayError):
    pass


class DeniedActionReachedGateway(ToolGatewayError):
    """Raised when a DENY path somehow reaches the gateway — invariant break."""


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


class ToolGateway:
    def __init__(
        self,
        ledger: EventLedger,
        token_service: ExecutionTokenService | None = None,
    ) -> None:
        self._ledger = ledger
        self._token_service = token_service or ExecutionTokenService()
        self._tools: dict[str, ToolHandler] = {}
        self._idempotency: dict[str, dict[str, Any]] = {}
        # Legacy deposit set — transitional only; prefer mint via ExecutionTokenService.
        self._legacy_tokens: set[str] = set()

    def register_tool(self, tool_id: str, handler: ToolHandler) -> None:
        self._tools[tool_id] = handler

    def accept_token(self, token: str) -> None:
        """DEPRECATED: deposit opaque string. Prefer proposal-bound ExecutionToken mint."""
        self._legacy_tokens.add(token)

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
    ) -> dict[str, Any]:
        if not execution_token:
            raise MissingExecutionToken("Tool Gateway requires execution token (GOS-I03)")

        token_refs: dict[str, str]
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
            if execution_token not in self._legacy_tokens:
                raise MissingExecutionToken(
                    "invalid, unbound, or already consumed execution token"
                ) from None
            self._legacy_tokens.discard(execution_token)
            token_refs = {
                "execution_token_id": "legacy",
                "execution_token_hash": content_hash(execution_token),
            }

        idem = proposal["idempotency_key"]
        if idem in self._idempotency:
            return self._idempotency[idem]

        handler = self._tools.get(tool_id)
        if handler is None:
            raise ToolGatewayError(f"unknown tool: {tool_id}")

        result = handler(proposal)
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
