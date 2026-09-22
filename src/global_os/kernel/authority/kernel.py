"""Authority Kernel — no model calls; default-deny; child ⊆ parent."""

from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal

from global_os.common.hashing import content_hash
from global_os.contracts.validate import validate
from global_os.kernel.authority.approvals import (
    ApprovalInvalid,
    ApprovalService,
    ApprovalToken,
)
from global_os.kernel.authority.execution_token import ExecutionTokenService, MintedExecutionToken
from global_os.kernel.policy import APPROVAL_REQUIRED, PolicyEngine, PolicyRequest
from global_os.runtime.events.ledger import EventLedger

AuthorityBackend = Literal["python", "rust"]


class Decision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    PENDING_APPROVAL = "PENDING_APPROVAL"


@dataclass(frozen=True)
class AuthzResult:
    decision: Decision
    reason: str
    execution_token: str | None = None
    proposal_hash: str | None = None
    execution_token_id: str | None = None
    execution_token_hash: str | None = None


class AuthorityKernel:
    """Deterministic authorization. Models are never invoked here (GOS-I01/I05)."""

    def __init__(
        self,
        ledger: EventLedger,
        policy: PolicyEngine | None = None,
        *,
        backend: AuthorityBackend | None = None,
        token_service: ExecutionTokenService | None = None,
        approval_service: ApprovalService | None = None,
    ) -> None:
        self._ledger = ledger
        self._policy = policy or PolicyEngine()
        self._grants: dict[str, frozenset[str]] = {}
        self._parents: dict[str, str] = {}
        self._token_service = token_service or ExecutionTokenService()
        self._approval_service = approval_service
        if backend is not None:
            self._backend = backend
        else:
            from global_os.runtime.profile import resolve_authority_backend

            env = os.environ.get("GOS_AUTHORITY_BACKEND")
            if env is not None and env not in {"python", "rust"}:
                raise ValueError(f"unsupported authority backend: {env}")
            self._backend = resolve_authority_backend()

    def grant(
        self,
        *,
        principal_id: str,
        capabilities: set[str],
        tenant_id: str,
        workspace_id: str,
        parent_id: str | None = None,
        goal_id: str | None = None,
    ) -> None:
        caps = frozenset(capabilities)
        if parent_id is not None:
            parent_caps = self._grants.get(parent_id, frozenset())
            if not caps.issubset(parent_caps):
                raise ValueError(
                    f"child authority must be ⊆ parent (GOS-I04): "
                    f"extra={sorted(caps - parent_caps)}"
                )
            self._parents[principal_id] = parent_id
        self._grants[principal_id] = caps
        self._ledger.append(
            event_type="authority.granted",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=goal_id,
            principal_id=principal_id,
            payload={
                "principal_id": principal_id,
                "capabilities": sorted(caps),
                "parent_id": parent_id,
            },
            producer="kernel.authority",
        )

    def decide(
        self,
        proposal: dict[str, Any],
        *,
        tenant_id: str,
        workspace_id: str,
        require_approval: bool = False,
    ) -> AuthzResult:
        validate(proposal, "action_proposal.schema.json")
        if self._backend == "rust":
            result = self._decide_rust(proposal, require_approval=require_approval)
            self._record_decision(result, proposal, tenant_id, workspace_id)
            return result
        return self._decide_python(
            proposal,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            require_approval=require_approval,
        )

    def _approval_action_hash(self, proposal: dict[str, Any]) -> str:
        """Bind approval to proposal fields excluding approval_token (chicken-egg safe)."""
        body = {k: v for k, v in proposal.items() if k != "approval_token"}
        return content_hash(body)

    def _consume_approval_if_required(
        self,
        proposal: dict[str, Any],
        *,
        proposal_hash: str,
        require_approval: bool,
    ) -> AuthzResult | None:
        """Hard-bind ApprovalService.verify_and_consume — approval_id string alone is insufficient."""
        capability = proposal["capability"]
        needs = require_approval or capability in APPROVAL_REQUIRED
        if not needs:
            return None

        token = self._extract_approval_token(proposal)
        if token is None:
            return AuthzResult(
                Decision.PENDING_APPROVAL,
                "approval required — ApprovalToken missing (approval_id string alone insufficient)",
                proposal_hash=proposal_hash,
            )
        if self._approval_service is None:
            return AuthzResult(
                Decision.DENY,
                "approval required but ApprovalService not configured",
                proposal_hash=proposal_hash,
            )
        try:
            self._approval_service.verify_and_consume(
                token,
                action_hash=self._approval_action_hash(proposal),
                goal_id=str(proposal["goal_id"]),
            )
        except ApprovalInvalid as exc:
            return AuthzResult(
                Decision.DENY,
                f"approval invalid: {exc}",
                proposal_hash=proposal_hash,
            )
        return None

    def _extract_approval_token(self, proposal: dict[str, Any]) -> ApprovalToken | None:
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

    def _mint_token(self, proposal: dict[str, Any], proposal_hash: str) -> MintedExecutionToken:
        return self._token_service.mint(proposal=proposal, proposal_hash=proposal_hash)

    def _decide_rust(self, proposal: dict[str, Any], *, require_approval: bool) -> AuthzResult:
        from global_os.adapters.authority import decide_via_rust

        principal = proposal["principal_id"]
        capability = proposal["capability"]
        granted = self._grants.get(principal, frozenset())
        parent_raw = proposal.get("parent_capabilities")
        proposal_hash = content_hash(proposal)
        approval_present = self._extract_approval_token(proposal) is not None
        # Capability / parent checks first (approval alone must not unlock missing grants)
        request = {
            "principal": principal,
            "action": capability,
            "capability": capability,
            "resource": str(proposal.get("resource", "")),
            "granted_capabilities": sorted(granted),
            "parent_capabilities": list(parent_raw) if parent_raw is not None else None,
            "approval_id": "verified" if approval_present else None,
        }
        raw = decide_via_rust(request, proposal)
        decision = Decision(raw["decision"])
        if decision != Decision.ALLOW:
            # Rust PENDING_APPROVAL → still hard-bind if we would otherwise allow
            if decision == Decision.PENDING_APPROVAL:
                blocked = self._consume_approval_if_required(
                    proposal, proposal_hash=proposal_hash, require_approval=True
                )
                if blocked is not None:
                    return blocked
                # verified — re-ask rust with presence flag
                request["approval_id"] = "verified"
                raw = decide_via_rust(request, proposal)
                decision = Decision(raw["decision"])
                if decision != Decision.ALLOW:
                    return AuthzResult(
                        decision,
                        str(raw.get("reason", "")),
                        proposal_hash=raw.get("proposal_hash") or proposal_hash,
                    )
            else:
                return AuthzResult(
                    decision,
                    str(raw.get("reason", "")),
                    proposal_hash=raw.get("proposal_hash") or proposal_hash,
                )
        else:
            blocked = self._consume_approval_if_required(
                proposal, proposal_hash=proposal_hash, require_approval=require_approval
            )
            if blocked is not None:
                return blocked

        minted = self._mint_token(proposal, proposal_hash)
        refs = self._token_service.ledger_refs(minted)
        return AuthzResult(
            Decision.ALLOW,
            str(raw.get("reason", "")),
            execution_token=minted.bearer,
            proposal_hash=proposal_hash,
            execution_token_id=refs["execution_token_id"],
            execution_token_hash=refs["execution_token_hash"],
        )

    def _decide_python(
        self,
        proposal: dict[str, Any],
        *,
        tenant_id: str,
        workspace_id: str,
        require_approval: bool,
    ) -> AuthzResult:
        proposal_hash = content_hash(proposal)
        principal = proposal["principal_id"]
        capability = proposal["capability"]
        granted = self._grants.get(principal, frozenset())
        parent_raw = proposal.get("parent_capabilities")
        parent_set = frozenset(parent_raw) if parent_raw is not None else None
        # Presence flag only for policy engine; hard verify happens separately
        approval_present = self._extract_approval_token(proposal) is not None

        policy = self._policy.decide(
            PolicyRequest(
                principal=principal,
                action=capability,
                resource=str(proposal.get("resource", "")),
                capability=capability,
                granted_capabilities=granted,
                parent_capabilities=parent_set,
                approval_id="verified" if approval_present else None,
            )
        )
        if not policy.allowed:
            decision = (
                Decision.PENDING_APPROVAL if "approval required" in policy.reason else Decision.DENY
            )
            result = AuthzResult(decision, policy.reason, proposal_hash=proposal_hash)
            self._record_decision(result, proposal, tenant_id, workspace_id)
            return result

        blocked = self._consume_approval_if_required(
            proposal, proposal_hash=proposal_hash, require_approval=require_approval
        )
        if blocked is not None:
            self._record_decision(blocked, proposal, tenant_id, workspace_id)
            return blocked

        minted = self._mint_token(proposal, proposal_hash)
        refs = self._token_service.ledger_refs(minted)
        result = AuthzResult(
            Decision.ALLOW,
            policy.reason,
            execution_token=minted.bearer,
            proposal_hash=proposal_hash,
            execution_token_id=refs["execution_token_id"],
            execution_token_hash=refs["execution_token_hash"],
        )
        self._record_decision(result, proposal, tenant_id, workspace_id)
        return result

    def _record_decision(
        self,
        result: AuthzResult,
        proposal: dict[str, Any],
        tenant_id: str,
        workspace_id: str,
    ) -> None:
        payload: dict[str, Any] = {
            "decision": result.decision.value,
            "reason": result.reason,
            "proposal_id": proposal.get("proposal_id"),
            "capability": proposal.get("capability"),
            "proposal_hash": result.proposal_hash,
            "backend": self._backend,
        }
        # Never write raw bearer into the ledger
        if result.execution_token_id is not None:
            payload["execution_token_id"] = result.execution_token_id
        if result.execution_token_hash is not None:
            payload["execution_token_hash"] = result.execution_token_hash
        self._ledger.append(
            event_type="authority.decision",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=proposal.get("goal_id"),
            principal_id=proposal.get("principal_id"),
            payload=payload,
            producer="kernel.authority",
        )


def memory_approval_service(signing_key: bytes | None = None) -> ApprovalService:
    """Test/helper: sqlite :memory: ApprovalService ready for AuthorityKernel."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE approvals (
            approval_id TEXT PRIMARY KEY,
            approver TEXT NOT NULL,
            action_hash TEXT NOT NULL,
            goal_id TEXT NOT NULL,
            limits_json TEXT NOT NULL,
            valid_until TEXT NOT NULL,
            one_time INTEGER NOT NULL,
            consumed INTEGER NOT NULL,
            signature TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return ApprovalService(conn, signing_key or b"gos-dev-approval-key")


def assert_no_model_imports() -> None:
    """Authority package must not import model adapters."""
    import sys

    banned = ("openai", "anthropic", "global_os.adapters.models")
    for name in banned:
        if name in sys.modules:
            raise RuntimeError(f"Authority Kernel must not load models: {name}")
