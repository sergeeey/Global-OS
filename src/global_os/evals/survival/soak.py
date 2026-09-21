"""Accelerated + schedule-driven GoalIntegritySurvival soak.

ACCELERATED: re-run full suite across ticks (CI).
SCHEDULED / WALL_CLOCK_48H: execute WALL_CLOCK_48H_SCHEDULE injections in order
at T+offset (real sleep when GOS_REQUIRE_48H=1; accelerated via GOS_SOAK_HOUR_SECONDS).
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any

from global_os.evals.integrity import (
    HARD_GATES,
    GateResult,
    SoftMetrics,
    all_pass_gates,
    score_goal_integrity,
)
from global_os.evals.survival.harness import run_injection, run_survival_suite
from global_os.evals.survival.scenarios import SurvivalReport
from global_os.evals.survival.wall_clock_schedule import WALL_CLOCK_48H_SCHEDULE, validate_schedule


@dataclass
class SoakReport:
    simulated_hours: float
    ticks: int
    wall_seconds: float
    fidelity: str
    tick_scores: list[float] = field(default_factory=list)
    final_goal_integrity_survival: float = 0.0
    passed: bool = False
    notes: str = ""
    schedule_results: list[dict[str, Any]] = field(default_factory=list)
    goal_integrity: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "simulated_hours": self.simulated_hours,
            "ticks": self.ticks,
            "wall_seconds": self.wall_seconds,
            "fidelity": self.fidelity,
            "tick_scores": list(self.tick_scores),
            "final_goal_integrity_survival": self.final_goal_integrity_survival,
            "passed": self.passed,
            "notes": self.notes,
            "schedule_results": list(self.schedule_results),
            "goal_integrity": self.goal_integrity,
        }


def _hour_seconds() -> float:
    """1.0 = real hour; CI uses small value for accelerated schedule."""
    return float(os.environ.get("GOS_SOAK_HOUR_SECONDS", "3600"))


def run_scheduled_48h_soak(*, sleep: bool = True) -> SoakReport:
    """Run preregistered WALL_CLOCK_48H_SCHEDULE injections in temporal order."""
    validate_schedule()
    require_wall = os.environ.get("GOS_REQUIRE_48H", "") == "1"
    hour_s = _hour_seconds()
    # Wall gate must use real hours unless explicitly overridden for dry-run
    if require_wall and hour_s < 3600 and os.environ.get("GOS_SOAK_ALLOW_FAST_WALL", "") != "1":
        hour_s = 3600.0
    fidelity = "WALL_CLOCK_48H" if require_wall and hour_s >= 3600 else "SCHEDULED_ACCELERATED"

    started = time.perf_counter()
    elapsed_target = 0.0
    results: list[dict[str, Any]] = []
    scores: list[float] = []

    for item in WALL_CLOCK_48H_SCHEDULE:
        target = item.offset_hours * hour_s
        if sleep and target > elapsed_target:
            time.sleep(target - elapsed_target)
            elapsed_target = target
        scenario = run_injection(item.injection)
        ok = scenario.passed is True
        scores.append(1.0 if ok else 0.0)
        results.append(
            {
                "offset_hours": item.offset_hours,
                "injection": item.injection.value,
                "description": item.description,
                "passed": scenario.passed,
                "notes": scenario.notes,
            }
        )
        if not ok:
            wall = time.perf_counter() - started
            gis = score_goal_integrity(
                {**{g: "PASS" for g in HARD_GATES}, "recovery_successful": "FAIL"},
                soft=SoftMetrics(recovery_events=len(results)),
                notes=f"injection failed at T+{item.offset_hours}h",
            )
            return SoakReport(
                simulated_hours=48.0,
                ticks=len(results),
                wall_seconds=wall,
                fidelity=fidelity,
                tick_scores=scores,
                final_goal_integrity_survival=sum(scores) / len(scores),
                passed=False,
                notes=f"schedule failure at T+{item.offset_hours}h ({item.injection.value})",
                schedule_results=results,
                goal_integrity=gis.as_dict(),
            )

    # Final integrity: all scheduled injections passed
    gates: dict[str, str | GateResult] = dict(all_pass_gates())
    gis = score_goal_integrity(
        gates,
        soft=SoftMetrics(recovery_events=len(results), completion=1.0),
        notes="scheduled 48h injections all passed",
    )
    wall = time.perf_counter() - started
    return SoakReport(
        simulated_hours=48.0,
        ticks=len(results),
        wall_seconds=wall,
        fidelity=fidelity,
        tick_scores=scores,
        final_goal_integrity_survival=1.0,
        passed=gis.survival == GateResult.PASS,
        notes=f"WALL_CLOCK schedule complete ({fidelity}); Goal Integrity PASS",
        schedule_results=results,
        goal_integrity=gis.as_dict(),
    )


def run_goal_integrity_soak(
    *,
    simulated_hours: float | None = None,
    ticks: int | None = None,
    sleep_per_tick: float = 0.0,
    use_schedule: bool | None = None,
) -> SoakReport:
    """Default: accelerated suite ticks. Schedule mode when requested or wall-clock."""
    require_wall = os.environ.get("GOS_REQUIRE_48H", "") == "1"
    if use_schedule is None:
        use_schedule = require_wall or os.environ.get("GOS_SOAK_USE_SCHEDULE", "") == "1"
    if use_schedule:
        return run_scheduled_48h_soak(sleep=sleep_per_tick > 0 or require_wall)

    sim_h = simulated_hours
    if sim_h is None:
        sim_h = float(os.environ.get("GOS_SOAK_SIMULATED_HOURS", "48"))
    n_ticks = ticks
    if n_ticks is None:
        n_ticks = int(os.environ.get("GOS_SOAK_TICKS", "24"))
    if n_ticks < 2:
        raise ValueError("soak requires ≥2 ticks")
    if sim_h < 24:
        raise ValueError("soak simulated horizon must be ≥24h (contract)")

    fidelity = "ACCELERATED_SIMULATED"
    if require_wall:
        fidelity = "WALL_CLOCK_48H"
        sleep_per_tick = max(sleep_per_tick, (48 * 3600) / n_ticks)

    started = time.perf_counter()
    scores: list[float] = []
    for i in range(n_ticks):
        report: SurvivalReport = run_survival_suite()
        score = report.goal_integrity_survival
        scores.append(score)
        if score < 1.0:
            wall = time.perf_counter() - started
            return SoakReport(
                simulated_hours=sim_h,
                ticks=i + 1,
                wall_seconds=wall,
                fidelity=fidelity,
                tick_scores=scores,
                final_goal_integrity_survival=score,
                passed=False,
                notes=f"survival regression at tick {i + 1}/{n_ticks}",
            )
        if sleep_per_tick > 0:
            time.sleep(sleep_per_tick)

    wall = time.perf_counter() - started
    final = scores[-1] if scores else 0.0
    return SoakReport(
        simulated_hours=sim_h,
        ticks=n_ticks,
        wall_seconds=wall,
        fidelity=fidelity,
        tick_scores=scores,
        final_goal_integrity_survival=final,
        passed=final == 1.0 and len(scores) == n_ticks,
        notes=(
            f"GoalIntegritySurvival=1.0 across {n_ticks} ticks "
            f"spanning simulated {sim_h}h ({fidelity})"
        ),
    )
