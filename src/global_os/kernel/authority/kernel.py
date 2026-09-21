"""Authority Kernel — no model calls; default-deny; child ⊆ parent."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from global_os.common.hashing import content_hash, new_id
from global_os.contracts.validate import validate
from global_os.kernel.policy import PolicyEngine, PolicyRequest
from global_os.runtime.events.ledger import EventLedger


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


class AuthorityKernel:
    """Deterministic authorization. Models are never invoked here (GOS-I01/I05)."""

    def __init__(self, ledger: EventLedger, policy: PolicyEngine | None = None) -> None:
        self._ledger = ledger
        self._policy = policy or PolicyEngine()
        # principal_id -> frozenset of capabilities
        self._grants: dict[str, frozenset[str]] = {}
        # parent_id -> child_id relationships for inheritance checks
        self._parents: dict[str, str] = {}

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
        proposal_hash = content_hash(proposal)
        principal = proposal["principal_id"]
        capability = proposal["capability"]
        granted = self._grants.get(principal, frozenset())
        parent_raw = proposal.get("parent_capabilities")
        parent_set = frozenset(parent_raw) if parent_raw is not None else None
        approval_refs = proposal.get("approval_refs") or []
        approval_id = approval_refs[0] if approval_refs else None

        policy = self._policy.decide(
            PolicyRequest(
                principal=principal,
                action=capability,
                resource=str(proposal.get("resource", "")),
                capability=capability,
                granted_capabilities=granted,
                parent_capabilities=parent_set,
                approval_id=approval_id,
            )
        )
        if not policy.allowed:
            decision = (
                Decision.PENDING_APPROVAL if "approval required" in policy.reason else Decision.DENY
            )
            result = AuthzResult(decision, policy.reason, proposal_hash=proposal_hash)
            self._record_decision(result, proposal, tenant_id, workspace_id)
            return result

        if require_approval and not approval_id:
            result = AuthzResult(
                Decision.PENDING_APPROVAL,
                "approval required",
                proposal_hash=proposal_hash,
            )
            self._record_decision(result, proposal, tenant_id, workspace_id)
            return result

        token = new_id("tok")
        result = AuthzResult(
            Decision.ALLOW,
            policy.reason,
            execution_token=token,
            proposal_hash=proposal_hash,
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
        self._ledger.append(
            event_type="authority.decision",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            goal_id=proposal.get("goal_id"),
            principal_id=proposal.get("principal_id"),
            payload={
                "decision": result.decision.value,
                "reason": result.reason,
                "proposal_id": proposal.get("proposal_id"),
                "capability": proposal.get("capability"),
                "proposal_hash": result.proposal_hash,
                "execution_token": result.execution_token,
            },
            producer="kernel.authority",
        )


# Sentinel: prove no LLM path exists
def assert_no_model_imports() -> None:
    """Authority package must not import model adapters."""
    import sys

    banned = ("openai", "anthropic", "global_os.adapters.models")
    for name in banned:
        if name in sys.modules:
            raise RuntimeError(f"Authority Kernel must not load models: {name}")
