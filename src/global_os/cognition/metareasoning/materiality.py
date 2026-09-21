"""Materiality engine — no fixed %-thresholds; task-sensitive (Impact×P×Irreversibility×GoalSensitivity)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MaterialityLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


_IMPACT = {"none": 0.0, "low": 0.25, "moderate": 0.5, "high": 0.8, "critical": 1.0}
_IRREV = {"none": 0.0, "low": 0.25, "moderate": 0.5, "high": 0.8, "critical": 1.0}


@dataclass(frozen=True)
class MaterialityAssessment:
    score: float
    level: MaterialityLevel
    ask_human: bool
    rationale: str


def assess_materiality(
    *,
    impact: str,
    probability: float,
    irreversibility: str,
    goal_sensitivity: float,
    ask_threshold: float = 0.35,
) -> MaterialityAssessment:
    """probability and goal_sensitivity in [0, 1]. No magic industry kappa/% rules."""
    p = max(0.0, min(1.0, probability))
    gs = max(0.0, min(1.0, goal_sensitivity))
    score = _IMPACT.get(impact, 0.5) * p * _IRREV.get(irreversibility, 0.5) * gs
    if score < 0.05:
        level = MaterialityLevel.NONE
    elif score < 0.2:
        level = MaterialityLevel.LOW
    elif score < 0.4:
        level = MaterialityLevel.MODERATE
    elif score < 0.7:
        level = MaterialityLevel.HIGH
    else:
        level = MaterialityLevel.CRITICAL
    return MaterialityAssessment(
        score=score,
        level=level,
        ask_human=score >= ask_threshold,
        rationale=(
            f"impact={impact} p={p:.2f} irrev={irreversibility} "
            f"goal_sens={gs:.2f} → {score:.3f}"
        ),
    )
