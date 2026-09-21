"""Wall-clock 48h operational injection schedule — release gate, not PR CI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from global_os.evals.survival.scenarios import Injection


@dataclass(frozen=True)
class ScheduledInjection:
    offset_hours: float
    injection: Injection
    description: str


# Pre-registered operational fault timeline (semantic integrity after 48h)
WALL_CLOCK_48H_SCHEDULE: tuple[ScheduledInjection, ...] = (
    ScheduledInjection(2.0, Injection.SLOW_DEPENDENCY, "model timeout"),
    ScheduledInjection(5.0, Injection.PROCESS_KILL, "worker kill"),
    ScheduledInjection(8.0, Injection.CONTRADICTORY_EVIDENCE, "contradictory evidence"),
    ScheduledInjection(12.0, Injection.MODEL_SWAP, "provider switch"),
    ScheduledInjection(18.0, Injection.BUDGET_REDUCTION, "budget cut"),
    ScheduledInjection(24.0, Injection.CONSTRAINT_CHANGE, "constraint amendment"),
    ScheduledInjection(30.0, Injection.API_OUTAGE, "sandbox/provider failure proxy"),
    ScheduledInjection(36.0, Injection.SOURCE_INVALIDATION, "evidence invalidation"),
    ScheduledInjection(42.0, Injection.CORRUPTED_STATE, "state projection rebuild / corrupt"),
)


def schedule_as_dict() -> dict[str, Any]:
    return {
        "name": "wall_clock_48h_operational",
        "duration_hours": 48.0,
        "ci_policy": "not_on_every_pr",
        "gates": {
            "pr": "normal_ci",
            "main": "integration",
            "nightly": "survival",
            "weekly_or_rc": "wall_clock_48h",
        },
        "injections": [
            {
                "offset_hours": s.offset_hours,
                "injection": s.injection.value,
                "description": s.description,
            }
            for s in WALL_CLOCK_48H_SCHEDULE
        ],
        "postcondition": "semantic_goal_integrity_pass",
        "notes": (
            "Accelerated soak ≠ wall-clock proof. Credentials expiry, network drift, "
            "connection decay, log growth require real time."
        ),
    }


def validate_schedule() -> None:
    hours = [s.offset_hours for s in WALL_CLOCK_48H_SCHEDULE]
    if hours != sorted(hours):
        raise ValueError("48h schedule must be time-ordered")
    if hours[-1] >= 48.0:
        raise ValueError("injections must complete before T+48h")
    if len({s.offset_hours for s in WALL_CLOCK_48H_SCHEDULE}) != len(hours):
        raise ValueError("duplicate injection offsets")
