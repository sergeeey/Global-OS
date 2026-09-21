"""H-RSN-001 synthetic harness — adaptive vs fixed-high reasoning budget.

Constraint checked: ReasoningBudget ≠ VerificationRequirement (GOS-I23).
Fidelity: synthetic_deterministic. Verdict never CONFIRMED from this harness alone.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

from global_os.cognition.metareasoning import ReasoningBudgetController

EFFORT_COST = {"low": 1.0, "medium": 2.0, "high": 4.0, "xhigh": 8.0, "max": 12.0}
EFFORT_QUALITY = {"low": 0.55, "medium": 0.72, "high": 0.85, "xhigh": 0.9, "max": 0.92}


@dataclass(frozen=True)
class BudgetTrial:
    policy: str
    effort: str
    quality: float
    cost: float
    quality_per_cost: float
    verification_tier: int


def _policy() -> dict[str, Any]:
    return {
        "default_effort": "low",
        "min_effort": "low",
        "max_effort": "high",
        "increase_when": ["verification_failed", "uncertainty_high", "task_high_impact"],
        "decrease_when": ["deterministic_task", "confidence_high", "cheap_verification_available"],
    }


def run_fixed_high(verification_tier: int = 2) -> BudgetTrial:
    effort = "high"
    q = EFFORT_QUALITY[effort]
    c = EFFORT_COST[effort]
    return BudgetTrial("fixed_high", effort, q, c, round(q / c, 4), verification_tier)


def run_adaptive(
    signals: set[str],
    verification_tier: int = 2,
) -> BudgetTrial:
    ctrl = ReasoningBudgetController()
    decision = ctrl.decide(_policy(), verification_tier=verification_tier, signals=signals)
    assert decision.verification_tier_unchanged == verification_tier
    effort = decision.effort
    q = EFFORT_QUALITY.get(effort, 0.5)
    c = EFFORT_COST.get(effort, 1.0)
    # Adaptive: easier tasks get lower cost with modest quality drop
    if "deterministic_task" in signals:
        q = min(q + 0.05, 0.8)  # cheap path still solves
    return BudgetTrial(
        "adaptive",
        effort,
        q,
        c,
        round(q / c, 4),
        decision.verification_tier_unchanged,
    )


def summarize_h_rsn_001() -> dict[str, Any]:
    fixed = run_fixed_high(verification_tier=3)
    easy = run_adaptive({"deterministic_task", "confidence_high"}, verification_tier=3)
    hard = run_adaptive({"verification_failed", "uncertainty_high"}, verification_tier=3)
    return {
        "id": "H-RSN-001",
        "hypothesis": "Dynamic reasoning allocation improves quality/cost vs fixed-high effort.",
        "fidelity": "synthetic_deterministic",
        "preregistered_at": "2026-09-21",
        "ran_at": datetime.now(UTC).isoformat(),
        "trials": {
            "fixed_high": asdict(fixed),
            "adaptive_easy": asdict(easy),
            "adaptive_hard": asdict(hard),
        },
        "gos_i23_holds": (
            fixed.verification_tier == 3
            and easy.verification_tier == 3
            and hard.verification_tier == 3
        ),
        "synthetic_hint_adaptive_qpc_better_on_easy": easy.quality_per_cost
        > fixed.quality_per_cost,
        "verdict": "INCONCLUSIVE_NEEDS_REAL_MODEL",
        "note": "Harness proves plumbing + GOS-I23; not scientific confirmation.",
    }
