"""48h GoalIntegritySurvival soak — accelerated by default; wall optional."""

from __future__ import annotations

import os

import pytest

from global_os.evals.survival.soak import run_goal_integrity_soak


def test_goal_integrity_soak_accelerated_48h_horizon(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("GOS_REQUIRE_48H", raising=False)
    monkeypatch.setenv("GOS_SOAK_SIMULATED_HOURS", "48")
    monkeypatch.setenv("GOS_SOAK_TICKS", "4")
    report = run_goal_integrity_soak(sleep_per_tick=0.0)
    assert report.passed is True
    assert report.simulated_hours == 48.0
    assert report.ticks == 4
    assert report.fidelity == "ACCELERATED_SIMULATED"
    assert report.final_goal_integrity_survival == 1.0
    assert all(s == 1.0 for s in report.tick_scores)
    assert "48.0h" in report.notes or "48h" in report.notes
    assert report.fidelity == "ACCELERATED_SIMULATED"


def test_soak_refuses_short_horizon():
    with pytest.raises(ValueError, match="≥24h"):
        run_goal_integrity_soak(simulated_hours=12, ticks=4)


def test_wall_clock_48h_gate_documented(monkeypatch: pytest.MonkeyPatch):
    """GOS_REQUIRE_48H would sleep ~48h — skip unless explicitly demanded."""
    if os.environ.get("GOS_REQUIRE_48H") == "1":
        report = run_goal_integrity_soak(ticks=2)
        assert report.fidelity == "WALL_CLOCK_48H"
        assert report.passed is True
    else:
        pytest.skip("wall-clock 48h not required (set GOS_REQUIRE_48H=1 to run)")
