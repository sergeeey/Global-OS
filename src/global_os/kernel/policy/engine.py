"""Deterministic policy engine mirroring Cedar default-deny semantics."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PolicyRequest:
    principal: str
    action: str
    resource: str
    capability: str
    granted_capabilities: frozenset[str]
    parent_capabilities: frozenset[str] | None = None
    approval_id: str | None = None


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str


# Actions that always require a non-empty approval_id
APPROVAL_REQUIRED = frozenset({"email.send", "payment.execute", "contract.sign"})

# Never permit these as cognitive-worker actions
FORBIDDEN_ACTIONS = frozenset({"everything", "admin", "Bash(*)", "bash.*"})


class PolicyEngine:
    """Cedar-aligned subset evaluated in-process until Rust/Cedar service lands."""

    def __init__(self, cedar_path: Path | None = None) -> None:
        self.cedar_path = cedar_path or (
            Path(__file__).resolve().parents[3] / "policies" / "cedar" / "base.cedar"
        )
        # Discover policies dir robustly
        if not self.cedar_path.exists():
            for parent in Path(__file__).resolve().parents:
                candidate = parent / "policies" / "cedar" / "base.cedar"
                if candidate.exists():
                    self.cedar_path = candidate
                    break

    def decide(self, request: PolicyRequest) -> PolicyDecision:
        if request.action in FORBIDDEN_ACTIONS or request.capability in FORBIDDEN_ACTIONS:
            return PolicyDecision(False, "forbidden wildcard/admin capability")
        if request.capability != request.action:
            return PolicyDecision(False, "action/capability mismatch")
        if request.capability not in request.granted_capabilities:
            return PolicyDecision(False, "capability not granted")
        if (
            request.parent_capabilities is not None
            and request.capability not in request.parent_capabilities
        ):
            return PolicyDecision(False, "capability not in parent authority (GOS-I04)")
        if request.action in APPROVAL_REQUIRED and not request.approval_id:
            return PolicyDecision(False, "approval required by policy")
        if not self.cedar_path.exists():
            return PolicyDecision(False, "cedar policy file missing — default deny")
        # Presence of base.cedar is required; evaluation is the deterministic subset above
        return PolicyDecision(True, "permitted by cedar-aligned policy")
