"""H-ORG split hypotheses H-ORG-1..4 — scientific claim not accepted from harness alone."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal

TaskClass = Literal["highly_parallel", "mixed_dependencies", "strongly_sequential"]
Topology = Literal[
    "strong_single",
    "manager_workers",
    "recursive_hierarchy",
    "hierarchy_plus_independent_verification",
    "adaptive",
]

HYPOTHESES: dict[str, str] = {
    "H-ORG-1": "Specialization beats identical general workers on heterogeneous tasks",
    "H-ORG-2": "Recursive hierarchy beats star topology after coordination scale threshold",
    "H-ORG-3": "Independent verification plane reduces escaped errors enough to justify cost",
    "H-ORG-4": (
        "Adaptive Organizational Compiler beats best fixed topology on mixed task "
        "distribution (E[Utility_Adaptive] > E[Utility_BestStatic]), not on every task"
    ),
}


@dataclass
class OrgConditionResult:
    topology: Topology
    task_class: TaskClass
    success: float
    cost: float
    escaped_errors: float
    information_loss: float
    utility: float


@dataclass
class HOrgFamilyReport:
    hypotheses: dict[str, str] = field(default_factory=lambda: dict(HYPOTHESES))
    conditions: list[OrgConditionResult] = field(default_factory=list)
    conditional_winners: dict[str, Topology] = field(default_factory=dict)
    distribution_winner: Topology | None = None
    scientific_claims_accepted: dict[str, bool] = field(
        default_factory=lambda: {k: False for k in HYPOTHESES}
    )
    verdict: str = "INCONCLUSIVE_NEEDS_LONG_HORIZON"
    fidelity: str = "synthetic_conditional"
    recorded_at: str = ""
    notes: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "hypotheses": self.hypotheses,
            "conditions": [asdict(c) for c in self.conditions],
            "conditional_winners": self.conditional_winners,
            "distribution_winner": self.distribution_winner,
            "scientific_claims_accepted": self.scientific_claims_accepted,
            "verdict": self.verdict,
            "fidelity": self.fidelity,
            "recorded_at": self.recorded_at,
            "notes": self.notes,
            "rule": (
                "Do not accept H-ORG because the pipeline runs; require long-horizon "
                "multi-class evidence. Adaptive must beat best static on distribution."
            ),
        }


def _utility(success: float, cost: float, escaped: float, info_loss: float) -> float:
    return success - 0.3 * escaped - 0.2 * info_loss - 0.05 * cost


def _synthetic_cell(topology: Topology, task_class: TaskClass) -> OrgConditionResult:
    """Honest synthetic priors for conditional patterns — not scientific confirmation."""
    # Expected qualitative pattern (documented as hypothesis prior, not proof)
    base = {
        ("strong_single", "strongly_sequential"): (0.88, 1.0, 0.05, 0.05),
        ("strong_single", "highly_parallel"): (0.55, 1.2, 0.15, 0.10),
        ("strong_single", "mixed_dependencies"): (0.70, 1.1, 0.10, 0.08),
        ("manager_workers", "highly_parallel"): (0.86, 1.4, 0.08, 0.12),
        ("manager_workers", "mixed_dependencies"): (0.80, 1.5, 0.09, 0.14),
        ("manager_workers", "strongly_sequential"): (0.72, 1.6, 0.08, 0.15),
        ("recursive_hierarchy", "mixed_dependencies"): (0.78, 2.1, 0.12, 0.25),
        ("recursive_hierarchy", "highly_parallel"): (0.75, 2.0, 0.14, 0.28),
        ("recursive_hierarchy", "strongly_sequential"): (0.65, 2.2, 0.16, 0.30),
        ("hierarchy_plus_independent_verification", "mixed_dependencies"): (0.82, 2.3, 0.04, 0.20),
        ("hierarchy_plus_independent_verification", "highly_parallel"): (0.80, 2.2, 0.05, 0.22),
        ("hierarchy_plus_independent_verification", "strongly_sequential"): (0.74, 2.4, 0.05, 0.22),
        ("adaptive", "highly_parallel"): (0.85, 1.45, 0.07, 0.12),
        ("adaptive", "mixed_dependencies"): (0.83, 1.7, 0.06, 0.15),
        ("adaptive", "strongly_sequential"): (0.86, 1.15, 0.05, 0.08),
    }
    success, cost, escaped, info_loss = base[(topology, task_class)]
    return OrgConditionResult(
        topology=topology,
        task_class=task_class,
        success=success,
        cost=cost,
        escaped_errors=escaped,
        information_loss=info_loss,
        utility=_utility(success, cost, escaped, info_loss),
    )


def summarize_horg_family() -> HOrgFamilyReport:
    topologies: tuple[Topology, ...] = (
        "strong_single",
        "manager_workers",
        "recursive_hierarchy",
        "hierarchy_plus_independent_verification",
        "adaptive",
    )
    classes: tuple[TaskClass, ...] = (
        "highly_parallel",
        "mixed_dependencies",
        "strongly_sequential",
    )
    conditions = [_synthetic_cell(t, c) for t in topologies for c in classes]
    winners: dict[str, Topology] = {}
    for c in classes:
        cells = [x for x in conditions if x.task_class == c]
        winners[c] = max(cells, key=lambda x: x.utility).topology

    # Distribution: equal mix of three classes — adaptive should be competitive
    dist_scores: dict[Topology, float] = {}
    for t in topologies:
        cells = [x for x in conditions if x.topology == t]
        dist_scores[t] = sum(x.utility for x in cells) / len(cells)
    distribution_winner = max(dist_scores, key=lambda k: dist_scores[k])

    return HOrgFamilyReport(
        conditions=conditions,
        conditional_winners=winners,
        distribution_winner=distribution_winner,
        scientific_claims_accepted={k: False for k in HYPOTHESES},
        verdict="SYNTHETIC_CONDITIONAL_MAP_NOT_PROOF",
        fidelity="synthetic_conditional",
        recorded_at=datetime.now(UTC).isoformat(),
        notes=(
            "Conditional winners illustrate expected heterogeneity; "
            "scientific acceptance requires live long-horizon multi-class runs (GOS-I30)."
        ),
    )
