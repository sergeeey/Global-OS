"""Acceptance guards for CHALLENGE-GA-v1 prereg lock (not execution)."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "artifacts" / "pilot" / "challenge_ga"
LOCK_PATH = PACK / "LOCK.json"
CONTRACT = PACK / "CHALLENGE_GA_CONTRACT.md"
TARGET = PACK / "TARGET.md"
RUBRIC = PACK / "SCORE_RUBRIC.md"
FIXTURE = PACK / "target_fixture" / "workload.py"
ORGANS_LOCK = ROOT / "artifacts" / "pilot" / "cognitive_core" / "organs" / "LOCK.json"


def _load_fixture():
    spec = importlib.util.spec_from_file_location("challenge_ga_workload", FIXTURE)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_challenge_ga_lock_sealed():
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    assert lock["protocol_id"] == "CHALLENGE-GA-v1"
    assert lock["status"] == "PREREG_LOCKED"
    assert lock["execution_status"] == "NOT_STARTED"
    assert lock["parent"]["pilot3_attr"] == "NOT_SHOWN"
    assert lock["parent"]["m2"] == "CLOSED"
    assert lock["parent"]["production_proven"] == 0
    assert lock["decisive_comparison"] == "C_vs_B"
    assert lock["terminal_success"]["sealed_checksum"] == 7674672
    assert lock["terminal_success"]["ops_budget_max"] == 80000
    assert lock["terminal_success"]["naive_ops_baseline"] == 160000
    assert "execute_before_human_request" in lock["forbidden"]
    assert "score_intermediate_plans_as_win" in lock["forbidden"]
    assert "soften_pilot3_attr" in lock["forbidden"]
    assert CONTRACT.is_file() and TARGET.is_file() and RUBRIC.is_file()
    assert FIXTURE.is_file()


def test_fixture_naive_baseline_matches_lock():
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    mod = _load_fixture()
    items = list(range(400))
    assert mod.process_items(items) == lock["terminal_success"]["sealed_checksum"]
    assert mod.last_ops() == lock["terminal_success"]["naive_ops_baseline"]
    # Budget is strictly harder than naive — WIN not free at lock
    assert mod.last_ops() > lock["terminal_success"]["ops_budget_max"]


def test_contract_terminal_win_and_stops():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "PREREG_LOCKED" in text
    assert "not executed" in text.lower() or "NOT_STARTED" in text
    assert "Terminal goal criterion" in text or "terminal Goal" in text.lower()
    for stop in (
        "STOP_SUCCESS",
        "STOP_BUDGET",
        "STOP_FORBIDDEN",
        "STOP_NO_STRATEGY",
        "STOP_ESCALATION",
        "INCONCLUSIVE",
    ):
        assert stop in text
    assert "intermediate" in text.lower()
    assert "NOT_SHOWN" in text
    assert "PRODUCTION_PROVEN" in text
    assert "C vs B" in text or "C_vs_B" in LOCK_PATH.read_text(encoding="utf-8")


def test_rubric_rejects_process_aesthetics_as_win():
    text = RUBRIC.read_text(encoding="utf-8")
    assert "Intermediate plans" in text or "intermediate plans" in text.lower()
    assert "≠ lines of ledger" in text or "lines of ledger" in text
    assert "H-GA-ATTR" in text


def test_organs_challenge_status_updated():
    organs = json.loads(ORGANS_LOCK.read_text(encoding="utf-8"))
    assert organs["status"] == "CONTRACTS_LOCKED"
    assert organs["challenge_status"] == "PREREG_LOCKED"
    assert organs["parent"]["pilot3_attr"] == "NOT_SHOWN"
    assert organs["parent"]["production_proven"] == 0


def test_capability_matrix_challenge_locked():
    matrix = json.loads((ROOT / "docs" / "capability_matrix.json").read_text(encoding="utf-8"))
    entry = matrix["research_campaigns"]["CHALLENGE_GA_V1"]
    assert entry["status"] == "PREREG_LOCKED"
    assert entry["execution_status"] == "NOT_STARTED"
    assert entry["pilot3_attr_preserved"] == "NOT_SHOWN"
    assert entry["m2_org_path"] == "CLOSED"
    assert entry["production_proven"] == 0
