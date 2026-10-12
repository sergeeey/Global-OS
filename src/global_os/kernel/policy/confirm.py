"""Deterministic risk assessment + confirmation policy (OpenHands shape, no LLM).

Assessment and enforcement are separate (ADR-0013). LLM-suggested security_risk
fields are ignored — GOS-I01 / forbidden LLM boolean security.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class SecurityRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"

    def is_riskier_than_or_equal(self, threshold: SecurityRisk) -> bool:
        order = {
            SecurityRisk.LOW: 0,
            SecurityRisk.MEDIUM: 1,
            SecurityRisk.HIGH: 2,
            SecurityRisk.UNKNOWN: 3,
        }
        return order[self] >= order[threshold]


# Deterministic tool-class heuristics (not LLM).
_HIGH_MARKERS = (
    "shell.exec",
    "bash",
    "process.kill",
    "fs.delete",
    "net.raw",
    "secret.",
    "credential",
    "docker.",
    "sudo",
)
_MEDIUM_MARKERS = (
    "fs.write",
    "fs.read",
    "http.",
    "email.send",
    "repo.push",
    "network",
)


@dataclass(frozen=True)
class RiskAssessment:
    risk: SecurityRisk
    reasons: tuple[str, ...]
    source: str = "deterministic_policy"

    def to_dict(self) -> dict[str, Any]:
        return {
            "risk": self.risk.value,
            "reasons": list(self.reasons),
            "source": self.source,
        }


def assess_action_risk(proposal: dict[str, Any]) -> RiskAssessment:
    """Assess risk from tool_id / action fields. Ignores any LLM security_risk."""
    # Explicitly discard LLM-provided scores (adversarial / OpenHands anti-pattern).
    _ = proposal.get("security_risk") or proposal.get("llm_security_risk")

    tool_id = str(proposal.get("tool_id") or proposal.get("action") or "").lower()
    args_blob = str(proposal.get("args") or proposal.get("arguments") or "").lower()
    network = str(proposal.get("network") or "").lower()
    blob = f"{tool_id} {args_blob} {network}"

    reasons: list[str] = []
    if any(m in blob for m in _HIGH_MARKERS):
        reasons.append("high_marker")
        return RiskAssessment(SecurityRisk.HIGH, tuple(reasons))
    if network and network not in ("none", "", "false"):
        reasons.append("network_enabled")
        return RiskAssessment(SecurityRisk.MEDIUM, tuple(reasons))
    if any(m in blob for m in _MEDIUM_MARKERS):
        reasons.append("medium_marker")
        return RiskAssessment(SecurityRisk.MEDIUM, tuple(reasons))
    if not tool_id:
        reasons.append("unknown_tool")
        return RiskAssessment(SecurityRisk.UNKNOWN, tuple(reasons))
    reasons.append("default_low")
    return RiskAssessment(SecurityRisk.LOW, tuple(reasons))


class ConfirmationPolicy(str, Enum):
    ALWAYS = "ALWAYS"
    NEVER = "NEVER"
    CONFIRM_RISKY = "CONFIRM_RISKY"


class ConfirmationRequired(Exception):
    """Raised when policy blocks execution pending human approval."""

    def __init__(self, assessment: RiskAssessment, policy: ConfirmationPolicy) -> None:
        self.assessment = assessment
        self.policy = policy
        super().__init__(
            f"confirmation required: risk={assessment.risk.value} policy={policy.value}"
        )


def requires_confirmation(
    assessment: RiskAssessment,
    policy: ConfirmationPolicy,
    *,
    threshold: SecurityRisk = SecurityRisk.HIGH,
    confirm_unknown: bool = True,
    approval_present: bool = False,
) -> bool:
    """Return True if execution must wait for approval (enforcement layer)."""
    if approval_present:
        return False
    if policy is ConfirmationPolicy.NEVER:
        return False
    if policy is ConfirmationPolicy.ALWAYS:
        return True
    # CONFIRM_RISKY
    if assessment.risk is SecurityRisk.UNKNOWN:
        return confirm_unknown
    return assessment.risk.is_riskier_than_or_equal(threshold)


def enforce_confirmation(
    proposal: dict[str, Any],
    policy: ConfirmationPolicy,
    *,
    approval_present: bool = False,
    threshold: SecurityRisk = SecurityRisk.HIGH,
) -> RiskAssessment:
    """Assess then enforce. Raises ConfirmationRequired when blocked."""
    assessment = assess_action_risk(proposal)
    if requires_confirmation(
        assessment,
        policy,
        threshold=threshold,
        approval_present=approval_present,
    ):
        raise ConfirmationRequired(assessment, policy)
    return assessment
