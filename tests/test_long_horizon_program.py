"""Long-horizon persistent research program — contract + preflight."""

from __future__ import annotations

import pytest

from global_os.evals.survival.research_program import (
    PASS_CRITERIA,
    PROGRAM_CONTRACT,
    REQUIRED_WALL_SECONDS_48H,
    evaluate_duration_gate,
    run_persistent_research_program,
    run_preflight,
)
from global_os.evals.survival.wall_clock_schedule import WALL_CLOCK_48H_SCHEDULE


def test_program_contract_frozen_pass_criteria():
    assert "wall_duration_meets_48h_contract" in PASS_CRITERIA
    assert len(PASS_CRITERIA) >= 11
    assert "goal_restored_after_restart" in PASS_CRITERIA
    assert "authority_does_not_self_expand" in PASS_CRITERIA
    d = PROGRAM_CONTRACT.as_dict()
    assert d["duration_hours"] == 48.0
    assert d["required_wall_seconds"] == REQUIRED_WALL_SECONDS_48H
    assert d["protocol_version"] == "LH-v2"
    assert "M1.5" in d["claims_forbidden"]
    assert d["scenario"][0].startswith("T0")


def test_duration_gate_rejects_42h_as_wall_clock_48h():
    """LH-FC-EARLY-STOP-42H: schedule complete at 42h must not claim WALL_CLOCK_48H PASS."""
    ok, fid, detail = evaluate_duration_gate(
        "wall_48h", hour_s=3600.0, wall_seconds=151200.19
    )
    assert ok is False
    assert fid == "WALL_CLOCK_EARLY_STOP"
    assert "<" in detail


def test_duration_gate_accepts_full_48h():
    ok, fid, _ = evaluate_duration_gate("wall_48h", hour_s=3600.0, wall_seconds=172800.0)
    assert ok is True
    assert fid == "WALL_CLOCK_48H"


def test_duration_gate_preflight_does_not_claim_48h():
    ok, fid, detail = evaluate_duration_gate("preflight", hour_s=0.0, wall_seconds=0.1)
    assert ok is True
    assert fid == "PREFLIGHT_COMPRESSED"
    assert "not claimed" in detail


def test_preflight_persistent_research_program(tmp_path):
    report = run_preflight(artifact_root=tmp_path / "preflight")
    assert report.mode == "preflight"
    assert report.fidelity == "PREFLIGHT_COMPRESSED"
    assert report.m15_claimed is False
    assert report.passed is True
    assert report.required_wall_seconds == REQUIRED_WALL_SECONDS_48H
    assert any(s.get("stage") == "terminal_barrier_t48" for s in report.stages)
    assert any(s.get("stage") == "shared_constraint_change" for s in report.stages)
    assert any(s.get("stage") == "shared_source_invalidation" for s in report.stages)
    assert len(report.schedule_results) == len(WALL_CLOCK_48H_SCHEDULE)
    assert all(r["passed"] for r in report.schedule_results)
    assert {c.id for c in report.criteria} == set(PASS_CRITERIA)
    assert all(c.passed for c in report.criteria)
    inv_c = next(c for c in report.criteria if c.id == "invalidated_evidence_propagates")
    assert inv_c.passed is True
    assert "STALE" in inv_c.detail
    assert report.goal_integrity is not None
    assert report.goal_integrity["survival"] == "PASS"
    assert report.goal_integrity["gates"]["goal_semantics_preserved"] == "PASS"
    assert report.goal_integrity["gates"]["budget_integrity"] == "PASS"
    assert (tmp_path / "preflight" / "program_report.json").is_file()
    assert (tmp_path / "preflight" / "program_contract.json").is_file()
    decisions = {m["mission_id"]: m["decision"] for m in report.mission_decisions}
    assert decisions["LH-1-parity-supported"] == "SUPPORTED"
    assert decisions["LH-2-null-preserved"] == "SUPPORTED"
    assert decisions["LH-3-post-fault-continue"] == "SUPPORTED"
    assert any(m["nulls"] > 0 for m in report.mission_decisions)
    assert report.provenance.get("protocol_version") == "LH-v2"


def test_wall_48h_refuses_without_double_gate(monkeypatch: pytest.MonkeyPatch, tmp_path):
    monkeypatch.delenv("GOS_REQUIRE_48H", raising=False)
    monkeypatch.delenv("GOS_START_RESEARCH_48H", raising=False)
    with pytest.raises(RuntimeError, match="GOS_REQUIRE_48H"):
        run_persistent_research_program(mode="wall_48h", artifact_root=tmp_path / "wall")

    monkeypatch.setenv("GOS_REQUIRE_48H", "1")
    with pytest.raises(RuntimeError, match="GOS_START_RESEARCH_48H"):
        run_persistent_research_program(mode="wall_48h", artifact_root=tmp_path / "wall")
