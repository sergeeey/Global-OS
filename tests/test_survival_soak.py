"""48h GoalIntegritySurvival soak — accelerated + scheduled modes."""

from __future__ import annotations

import os

import pytest

from global_os.evals.survival.soak import run_goal_integrity_soak, run_scheduled_48h_soak
from global_os.evals.survival.wall_clock_schedule import WALL_CLOCK_48H_SCHEDULE


def test_goal_integrity_soak_accelerated_48h_horizon(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("GOS_REQUIRE_48H", raising=False)
    monkeypatch.delenv("GOS_SOAK_USE_SCHEDULE", raising=False)
    monkeypatch.setenv("GOS_SOAK_SIMULATED_HOURS", "48")
    monkeypatch.setenv("GOS_SOAK_TICKS", "4")
    report = run_goal_integrity_soak(sleep_per_tick=0.0, use_schedule=False)
    assert report.passed is True
    assert report.simulated_hours == 48.0
    assert report.ticks == 4
    assert report.fidelity == "ACCELERATED_SIMULATED"
    assert report.final_goal_integrity_survival == 1.0
    assert all(s == 1.0 for s in report.tick_scores)
    assert "48.0h" in report.notes or "48h" in report.notes


def test_scheduled_48h_soak_accelerated_follows_preregistered_timeline(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.delenv("GOS_REQUIRE_48H", raising=False)
    monkeypatch.setenv("GOS_SOAK_HOUR_SECONDS", "0")
    report = run_scheduled_48h_soak(sleep=False)
    assert report.passed is True
    assert report.fidelity == "SCHEDULED_ACCELERATED"
    assert len(report.schedule_results) == len(WALL_CLOCK_48H_SCHEDULE)
    assert report.schedule_results[0]["offset_hours"] == 2.0
    assert report.schedule_results[-1]["offset_hours"] == 42.0
    assert all(r["passed"] is True for r in report.schedule_results)
    assert report.goal_integrity is not None
    assert report.goal_integrity["survival"] == "PASS"


def test_soak_refuses_short_horizon():
    with pytest.raises(ValueError, match="≥24h"):
        run_goal_integrity_soak(simulated_hours=12, ticks=4, use_schedule=False)


def test_wall_clock_48h_gate_documented(monkeypatch: pytest.MonkeyPatch):
    """GOS_REQUIRE_48H would sleep ~48h — skip unless explicitly demanded."""
    if os.environ.get("GOS_REQUIRE_48H") == "1":
        report = run_goal_integrity_soak(use_schedule=True)
        assert (
            report.fidelity.startswith("WALL_CLOCK") or report.fidelity == "SCHEDULED_ACCELERATED"
        )
        assert report.passed is True
    else:
        pytest.skip("wall-clock 48h not required (set GOS_REQUIRE_48H=1 to run)")
