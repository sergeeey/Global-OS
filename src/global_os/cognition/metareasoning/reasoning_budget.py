"""Reasoning budget controller — compute allocation only; never lowers verification (GOS-I23)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

EFFORT_ORDER = ("none", "low", "medium", "high", "xhigh", "max")


@dataclass(frozen=True)
class EffortDecision:
    effort: str
    verification_tier_unchanged: int
    reason: str


class ReasoningBudgetController:
    def decide(
        self,
        budget: dict[str, Any],
        *,
        verification_tier: int,
        signals: set[str],
    ) -> EffortDecision:
        """signals may include confidence_high — may decrease effort, never verification."""
        default = budget.get("default_effort", "low")
        min_e = budget.get("min_effort", "none")
        max_e = budget.get("max_effort", "high")
        effort = default

        increase = set(budget.get("increase_when", []))
        decrease = set(budget.get("decrease_when", []))

        if signals & increase:
            effort = _bump(effort, +1, min_e, max_e)
            reason = f"increase due to {sorted(signals & increase)}"
        elif signals & decrease:
            effort = _bump(effort, -1, min_e, max_e)
            reason = f"decrease due to {sorted(signals & decrease)}"
        else:
            reason = "default effort"

        # GOS-I23: verification tier is an input, never mutated here
        return EffortDecision(
            effort=effort,
            verification_tier_unchanged=verification_tier,
            reason=reason,
        )


def _bump(current: str, delta: int, min_e: str, max_e: str) -> str:
    lo = EFFORT_ORDER.index(min_e) if min_e in EFFORT_ORDER else 0
    hi = EFFORT_ORDER.index(max_e) if max_e in EFFORT_ORDER else len(EFFORT_ORDER) - 1
    idx = EFFORT_ORDER.index(current) if current in EFFORT_ORDER else lo
    idx = max(lo, min(hi, idx + delta))
    return EFFORT_ORDER[idx]
