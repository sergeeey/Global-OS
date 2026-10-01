"""Acceptance: external dual missions + M-EXT1/M-EXT2 terminals."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "artifacts" / "external"


def test_external_contract_locked() -> None:
    raw = json.loads((EXT / "CONTRACT" / "EXTERNAL_REAL_WORK.json").read_text(encoding="utf-8"))
    assert raw["status"] == "CONTRACT_LOCKED"
    assert "EW1" in raw["missions"] and "EW2" in raw["missions"]


def test_m_ext1_immutable() -> None:
    closed = json.loads((EXT / "M_EXT1_EW2_EXAM" / "M_EXT1_CLOSED.json").read_text(encoding="utf-8"))
    assert closed["status"] == "IMMUTABLE_TERMINAL"
    assert closed["terminal"] == "ROOT_CAUSE_CONFIRMED"
    assert closed["architecture_changes"] == "NONE"
    assert closed["gos_self_score_polish_forbidden"] is True
    assert "IMMUTABLE" in (EXT / "M_EXT1_EW2_EXAM" / "M_EXT1_CLOSED.md").read_text(encoding="utf-8")


def test_m_ext1_ew2_exam_terminal() -> None:
    exam = EXT / "M_EXT1_EW2_EXAM"
    goal = (exam / "GOAL_CONTRACT.md").read_text(encoding="utf-8")
    assert "Time / budget" in goal or "budget envelope" in goal.lower()
    ledger = json.loads((exam / "MISSION_LEDGER.json").read_text(encoding="utf-8"))
    assert ledger["terminal_verdict"] == "ROOT_CAUSE_CONFIRMED"
    assert ledger["gos_modified"] is False
    before = (
        EXT / "EW2_oss_incident" / "repro" / "logs" / "regression_BEFORE_patch.txt"
    ).read_text(encoding="utf-8")
    after = (
        EXT / "EW2_oss_incident" / "repro" / "logs" / "regression_AFTER_patch.txt"
    ).read_text(encoding="utf-8")
    assert "FAILED" in before
    assert "2 passed" in after


def test_m_ext2_ew1_inconclusive_no_retune() -> None:
    closed = json.loads((EXT / "M_EXT2_EW1_EXAM" / "M_EXT2_CLOSED.json").read_text(encoding="utf-8"))
    assert closed["status"] == "CAMPAIGN_CLOSED"
    assert closed["terminal"] == "INCONCLUSIVE"
    assert closed["post_hoc_retune"] is False
    score = json.loads((EXT / "EW1_transient_predictor" / "SCORE_RAW.json").read_text(encoding="utf-8"))
    assert score["decision"]["verdict"] == "INCONCLUSIVE"
    assert score["gos_architecture_changed"] is False
    assert score["not_y19_reopen"] is True
    bal = score["decision"]["holdout_balance"]
    assert bal["neg"] == 0
    decision = (EXT / "EW1_transient_predictor" / "EW1_DECISION.md").read_text(encoding="utf-8")
    assert "INCONCLUSIVE" in decision


def test_y24_y25_remain_closed() -> None:
    y24 = json.loads((ROOT / "artifacts" / "y24" / "Y24_CLOSED.json").read_text(encoding="utf-8"))
    y25 = json.loads((ROOT / "artifacts" / "y25" / "Y25_CLOSED.json").read_text(encoding="utf-8"))
    assert y24["status"] == "CAMPAIGN_CLOSED"
    assert y25["status"] == "CAMPAIGN_CLOSED"
