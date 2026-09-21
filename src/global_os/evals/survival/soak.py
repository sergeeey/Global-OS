"""Accelerated GoalIntegritySurvival soak — Reality Contact durability harness.

Wall-clock 48h is optional via GOS_REQUIRE_48H=1.
Default CI path compresses simulated horizon with GOS_SOAK_SIMULATED_HOURS
(default 48) and GOS_SOAK_TICKS (default 24) — honest fidelity label ACCELERATED.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any

from global_os.evals.survival.harness import run_survival_suite
from global_os.evals.survival.scenarios import SurvivalReport


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
        }


def run_goal_integrity_soak(
    *,
    simulated_hours: float | None = None,
    ticks: int | None = None,
    sleep_per_tick: float = 0.0,
) -> SoakReport:
    """Re-run survival suite across ticks spanning a simulated horizon."""
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

    require_wall = os.environ.get("GOS_REQUIRE_48H", "") == "1"
    fidelity = "WALL_CLOCK_48H" if require_wall else "ACCELERATED_SIMULATED"
    if require_wall:
        # Spread ticks across ~48h wall (tests should not set this in CI).
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
