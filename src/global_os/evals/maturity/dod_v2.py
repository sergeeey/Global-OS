"""DoD Architecture V2 evidence gate — formal existence ≠ E2E adversarial proof."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class DodStatus(str, Enum):
    PASS = "PASS"
    PARTIAL = "PARTIAL"
    FAIL = "FAIL"
    UNPROVEN = "UNPROVEN"


@dataclass(frozen=True)
class DodItem:
    id: str
    requirement: str
    status: DodStatus
    evidence: str


# Honest inventory: code+tests exist for many; live/adversarial long-horizon still open.
DOD_V2_ITEMS: tuple[DodItem, ...] = (
    DodItem(
        "goal_immutable",
        "GoalContract immutable/versioned",
        DodStatus.PASS,
        "GoalStore amend creates new version; tests/test_goal_and_events.py",
    ),
    DodItem(
        "goal_amendments_audited",
        "Goal amendments audited",
        DodStatus.PASS,
        "goal.amended events on ledger",
    ),
    DodItem(
        "epistemic_separation",
        "Observed/Belief/Hypothesis/Forecast/Decision/Commitment separated",
        DodStatus.PASS,
        "EpistemicStore typed nodes; tests/test_epistemic.py",
    ),
    DodItem(
        "invalidation_propagates",
        "Epistemic invalidation propagates downstream",
        DodStatus.PASS,
        "GOS-I12 chain; survival SOURCE_INVALIDATION",
    ),
    DodItem(
        "authority_non_bypass",
        "Authority Kernel cannot be bypassed",
        DodStatus.PARTIAL,
        "default-deny + Rust boundary; live adversarial long-horizon UNPROVEN",
    ),
    DodItem(
        "scoped_execution_token",
        "ExecutionToken scoped + short-lived",
        DodStatus.PASS,
        "ToolGateway token gate; tests/test_authority.py",
    ),
    DodItem(
        "effect_receipt",
        "Material actions have EffectContract + EffectReceipt",
        DodStatus.PASS,
        "ToolGateway EffectReceipt + discrepancy; FALSE_TOOL_SUCCESS survival",
    ),
    DodItem(
        "environment_compiler_selects",
        "EnvironmentCompiler actually selects environment",
        DodStatus.PARTIAL,
        "deterministic compile + ChangeGate; live H-ENV ladder still wire/prompt-conditioned",
    ),
    DodItem(
        "org_unit_recursive",
        "OrganizationalUnit is generic/recursive",
        DodStatus.PARTIAL,
        "OrgCompiler topologies contracted; recursive superiority UNPROVEN (GOS-I30)",
    ),
    DodItem(
        "verification_independent",
        "Verification Plane independent from execution",
        DodStatus.PARTIAL,
        "IndependentVerificationStack + multi-provider adapters; live diversity limited",
    ),
    DodItem(
        "external_tainted",
        "External content tainted",
        DodStatus.PASS,
        "GOS-I26; MALICIOUS_DOCUMENT survival",
    ),
    DodItem(
        "reasoning_ne_verification",
        "ReasoningBudget != VerificationRequirement",
        DodStatus.PASS,
        "GOS-I23; H-RSN harness + MODEL_SWAP survival",
    ),
    DodItem(
        "replay_canonical",
        "Replay reconstructs canonical state",
        DodStatus.PARTIAL,
        "EventReplayEngine status projection; full entity-body snapshot restore not claimed",
    ),
    DodItem(
        "maturity_from_evidence",
        "Capability maturity derived from evidence",
        DodStatus.PASS,
        "capability_matrix + self-audit; CLAIM OVERSTATED detection",
    ),
)


def summarize_dod_v2() -> dict[str, Any]:
    items = list(DOD_V2_ITEMS)
    counts = {s.value: sum(1 for i in items if i.status == s) for s in DodStatus}
    all_pass = all(i.status == DodStatus.PASS for i in items)
    return {
        "milestone": "DoD_V2",
        "closed": False,  # refuse silent close while any PARTIAL/UNPROVEN/FAIL
        "all_pass": all_pass,
        "counts": counts,
        "items": [asdict(i) | {"status": i.status.value} for i in items],
        "rule": (
            "Formal code existence ≠ DoD V2. Any PARTIAL/UNPROVEN blocks closure. "
            "Close only after integration+adversarial runtime paths for every item."
        ),
        "recorded_at": datetime.now(UTC).isoformat(),
        "depends_on": "M1.5_OPERATIONALY_VALIDATED",
    }
