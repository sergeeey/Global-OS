"""Acceptance + adversarial tests for ARCH-ABLATION-MECH-v1."""

from __future__ import annotations

import json
from pathlib import Path

from global_os.evals.research.arch_ablation import (
    ARM_IDS,
    ARTIFACT_ROOT,
    PROTOCOL_ID,
    SCENARIO_IDS,
    run_ablation,
    run_arm_scenario,
    write_scoreboard,
)

LOCK_PATH = ARTIFACT_ROOT / "LOCK.json"


def test_lock_pack_sealed():
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    assert lock["protocol_id"] == PROTOCOL_ID
    assert lock["status"] == "LOCKED"
    assert lock["fidelity"] == "SCRIPTED_MECHANISM_ABLATION"
    assert lock["scenarios"] == list(SCENARIO_IDS)
    assert set(lock["arms"]) == set(ARM_IDS)
    assert lock["parent"]["gos_incremental"] == "NOT_SHOWN"
    assert lock["parent"]["m2"] == "CLOSED"
    assert lock["parent"]["production_proven"] == 0
    for name in (
        "PREREG.md",
        "METRICS.md",
        "SCENARIOS.md",
        "FIDELITY.md",
        "GOAL_CONTRACT.md",
        "README.md",
    ):
        assert (ARTIFACT_ROOT / name).is_file(), name


def test_b0_fails_all_sealed_stress_classes(tmp_path: Path):
    for scenario in SCENARIO_IDS:
        row = run_arm_scenario("B0", scenario, tmp_path / "B0" / scenario)
        assert row.invariant_held is False, scenario
        assert row.failure_modes, scenario


def test_g1_holds_goal_and_ledger_not_effect(tmp_path: Path):
    s1 = run_arm_scenario("G1", "S1", tmp_path / "g1s1")
    s2 = run_arm_scenario("G1", "S2", tmp_path / "g1s2")
    s4 = run_arm_scenario("G1", "S4", tmp_path / "g1s4")
    assert s1.invariant_held and not s1.failure_modes
    assert s2.invariant_held and not s2.failure_modes
    assert s4.invariant_held is False
    assert "false_world_success" in s4.failure_modes


def test_g2_catches_false_world_success(tmp_path: Path):
    s4 = run_arm_scenario("G2", "S4", tmp_path / "g2s4")
    assert s4.invariant_held
    assert "false_world_success" not in s4.failure_modes


def test_g3_denies_privilege_expansion_g2_does_not(tmp_path: Path):
    g2 = run_arm_scenario("G2", "S3", tmp_path / "g2s3")
    g3 = run_arm_scenario("G3", "S3", tmp_path / "g3s3")
    assert "privilege_expansion" in g2.failure_modes
    assert "privilege_expansion" not in g3.failure_modes


def test_gfull_holds_s3_fully(tmp_path: Path):
    row = run_arm_scenario("Gfull", "S3", tmp_path / "gfulls3")
    assert row.invariant_held
    assert not row.failure_modes


def test_full_ablation_scoreboard_and_parent_invariants(tmp_path: Path):
    result = run_ablation(tmp_path / "run")
    assert result["protocol_id"] == PROTOCOL_ID
    assert len(result["rows"]) == len(ARM_IDS) * len(SCENARIO_IDS)
    agg = result["aggregate"]
    assert agg["arms"]["B0"]["scenarios_held_count"] == 0
    assert agg["arms"]["G1"]["wins_vs_B0"] is True
    assert agg["arms"]["G2"]["wins_vs_B0"] is True
    assert agg["arms"]["G3"]["wins_vs_B0"] is True
    assert agg["arms"]["Gfull"]["wins_vs_B0"] is True
    assert "S3" in agg["arms"]["Gfull"]["scenarios_held"]
    assert agg["hypotheses"]["H-ABL-G1"] == "SUPPORTED"
    assert agg["hypotheses"]["H-ABL-G2"] == "SUPPORTED"
    assert agg["hypotheses"]["H-ABL-G3"] == "SUPPORTED"
    assert agg["hypotheses"]["H-ABL-Gfull"] == "SUPPORTED"
    assert agg["parent_invariants"]["gos_incremental"] == "NOT_SHOWN"
    assert agg["parent_invariants"]["m2"] == "CLOSED"
    assert agg["parent_invariants"]["production_proven"] == 0

    out = write_scoreboard(result, tmp_path / "SCOREBOARD.json")
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["aggregate"]["hypotheses"]["H-ABL-ATTR-PRESERVE"] == "SUPPORTED"


def test_adversarial_no_scenario_skipped(tmp_path: Path):
    result = run_ablation(tmp_path / "adv")
    seen = {(r["arm_id"], r["scenario_id"]) for r in result["rows"]}
    expected = {(a, s) for a in ARM_IDS for s in SCENARIO_IDS}
    assert seen == expected
