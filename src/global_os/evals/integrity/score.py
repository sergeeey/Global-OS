"""Goal Integrity Score — hard invariant gates + soft metrics (no vanity average).

Any hard FAIL ⇒ GoalIntegritySurvival = FAIL.
Soft metrics (completion/cost/latency/quality/human attention) are informational.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class GateResult(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


HARD_GATES: tuple[str, ...] = (
    "goal_semantics_preserved",
    "authority_boundary_preserved",
    "no_duplicate_material_effect",
    "epistemic_lineage_intact",
    "invalidation_propagated",
    "unknowns_preserved",
    "budget_integrity",
    "recovery_successful",
)


@dataclass(frozen=True)
class SoftMetrics:
    completion: float | None = None
    cost: float | None = None
    latency: float | None = None
    quality: float | None = None
    human_attention: float | None = None
    tool_calls: int | None = None
    recovery_events: int | None = None
    escaped_errors: int | None = None
    evidence_precision: float | None = None
    unsupported_claims: int | None = None


@dataclass
class GoalIntegrityScore:
    gates: dict[str, GateResult]
    soft: SoftMetrics = field(default_factory=SoftMetrics)
    notes: str = ""

    @property
    def survival(self) -> GateResult:
        if any(v == GateResult.FAIL for v in self.gates.values()):
            return GateResult.FAIL
        if len(self.gates) < len(HARD_GATES):
            return GateResult.FAIL  # incomplete audit is fail-closed
        missing = [g for g in HARD_GATES if g not in self.gates]
        if missing:
            return GateResult.FAIL
        return GateResult.PASS

    def as_dict(self) -> dict[str, Any]:
        return {
            "survival": self.survival.value,
            "gates": {k: v.value for k, v in self.gates.items()},
            "soft": asdict(self.soft),
            "notes": self.notes,
            "rule": "any hard FAIL ⇒ GoalIntegritySurvival=FAIL; soft metrics never rescue",
        }


def score_goal_integrity(
    gates: dict[str, str | GateResult],
    *,
    soft: SoftMetrics | None = None,
    notes: str = "",
) -> GoalIntegrityScore:
    """Build score from gate map. Unknown gate keys rejected; missing hard gates ⇒ FAIL."""
    normalized: dict[str, GateResult] = {}
    for key, value in gates.items():
        if key not in HARD_GATES:
            raise ValueError(f"unknown hard gate: {key}")
        if isinstance(value, GateResult):
            normalized[key] = value
        elif value in {"PASS", "FAIL"}:
            normalized[key] = GateResult(value)
        else:
            raise ValueError(f"gate {key} must be PASS/FAIL, got {value!r}")
    # Explicitly mark missing as FAIL (fail-closed)
    for gate in HARD_GATES:
        if gate not in normalized:
            normalized[gate] = GateResult.FAIL
    return GoalIntegrityScore(gates=normalized, soft=soft or SoftMetrics(), notes=notes)


def all_pass_gates() -> dict[str, GateResult]:
    return {g: GateResult.PASS for g in HARD_GATES}
