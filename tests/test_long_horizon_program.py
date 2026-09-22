"""Long-horizon persistent research program — contract + preflight."""

from __future__ import annotations

import pytest

from global_os.evals.survival.research_program import (
    PASS_CRITERIA,
    PROGRAM_CONTRACT,
    run_persistent_research_program,
    run_preflight,
)
from global_os.evals.survival.wall_clock_schedule import WALL_CLOCK_48H_SCHEDULE


def test_program_contract_frozen_pass_criteria():
    assert len(PASS_CRITERIA) >= 10
    assert "goal_restored_after_restart" in PASS_CRITERIA
    assert "authority_does_not_self_expand" in PASS_CRITERIA
    d = PROGRAM_CONTRACT.as_dict()
    assert d["duration_hours"] == 48.0
    assert "M1.5" in d["claims_forbidden"]
    assert d["scenario"][0].startswith("T0")


def test_preflight_persistent_research_program(tmp_path):
    report = run_preflight(artifact_root=tmp_path / "preflight")
    assert report.mode == "preflight"
    assert report.fidelity == "PREFLIGHT_COMPRESSED"
    assert report.m15_claimed is False
    assert report.passed is True
    assert len(report.schedule_results) == len(WALL_CLOCK_48H_SCHEDULE)
    assert all(r["passed"] for r in report.schedule_results)
    assert {c.id for c in report.criteria} == set(PASS_CRITERIA)
    assert all(c.passed for c in report.criteria)
    assert report.goal_integrity is not None
    assert report.goal_integrity["survival"] == "PASS"
    assert (tmp_path / "preflight" / "program_report.json").is_file()
    assert (tmp_path / "preflight" / "program_contract.json").is_file()
    decisions = {m["mission_id"]: m["decision"] for m in report.mission_decisions}
    assert decisions["LH-1-parity-supported"] == "SUPPORTED"
    assert decisions["LH-2-null-preserved"] == "SUPPORTED"
    assert decisions["LH-3-post-fault-continue"] == "SUPPORTED"
    assert any(m["nulls"] > 0 for m in report.mission_decisions)


def test_wall_48h_refuses_without_double_gate(monkeypatch: pytest.MonkeyPatch, tmp_path):
    monkeypatch.delenv("GOS_REQUIRE_48H", raising=False)
    monkeypatch.delenv("GOS_START_RESEARCH_48H", raising=False)
    with pytest.raises(RuntimeError, match="GOS_REQUIRE_48H"):
        run_persistent_research_program(mode="wall_48h", artifact_root=tmp_path / "wall")

    monkeypatch.setenv("GOS_REQUIRE_48H", "1")
    with pytest.raises(RuntimeError, match="GOS_START_RESEARCH_48H"):
        run_persistent_research_program(mode="wall_48h", artifact_root=tmp_path / "wall")
