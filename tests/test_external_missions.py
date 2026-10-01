"""Acceptance: external dual missions locked; not GOS self-proof."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "artifacts" / "external"


def test_external_contract_locked() -> None:
    raw = json.loads((EXT / "CONTRACT" / "EXTERNAL_REAL_WORK.json").read_text(encoding="utf-8"))
    assert raw["status"] == "CONTRACT_LOCKED"
    assert "EW1" in raw["missions"] and "EW2" in raw["missions"]
    assert "cite_y24_or_y25_as_evidence_for_external_hypothesis" in raw["forbidden"]
    assert (EXT / "CONTRACT" / "EXTERNAL_REAL_WORK.md").is_file()


def test_ew1_prereg_not_y19_reopen() -> None:
    raw = json.loads(
        (EXT / "EW1_transient_predictor" / "EW1-PREREG.json").read_text(encoding="utf-8")
    )
    assert raw["status"] == "PREREG_LOCKED"
    assert raw["protocol_id"] == "EW1-CTP-v1"
    assert raw["not_y19_reopen"] is True
    assert raw["y19_y24_y25_not_evidence"] is True
    assert raw["arms_started"] is False
    assert raw["holdout_status"] == "NOT_SEALED_YET"
    assert len(raw["hypotheses"]) == 3
    y19 = (ROOT / "artifacts" / "y19" / "CLAIMS.md").read_text(encoding="utf-8")
    assert "FROZEN" in y19


def test_ew2_urllib3_issue_pinned() -> None:
    raw = json.loads((EXT / "EW2_oss_incident" / "EW2-PREREG.json").read_text(encoding="utf-8"))
    pin = json.loads((EXT / "EW2_oss_incident" / "EW2_PIN.json").read_text(encoding="utf-8"))
    assert raw["status"] == "PREREG_LOCKED"
    assert raw["target"]["issue_number"] == 5248
    assert raw["target"]["repo"] == "urllib3/urllib3"
    assert pin["issue_number"] == 5248
    assert pin["urllib3_head_sha_at_pin"]
    assert raw["investigation_started"] is True
    assert raw.get("terminal_verdict") == "ROOT_CAUSE_CONFIRMED"
    assert (EXT / "EW2_oss_incident" / "ISSUE_SNAPSHOT.json").is_file()


def test_y24_y25_remain_closed() -> None:
    y24 = json.loads((ROOT / "artifacts" / "y24" / "Y24_CLOSED.json").read_text(encoding="utf-8"))
    y25 = json.loads((ROOT / "artifacts" / "y25" / "Y25_CLOSED.json").read_text(encoding="utf-8"))
    assert y24["status"] == "CAMPAIGN_CLOSED"
    assert y25["status"] == "CAMPAIGN_CLOSED"
    assert y25["y25_f2"] == "FORBIDDEN_NOW"


def test_m_ext1_ew2_exam_terminal() -> None:
    exam = EXT / "M_EXT1_EW2_EXAM"
    goal = (exam / "GOAL_CONTRACT.md").read_text(encoding="utf-8")
    assert "budget envelope" in goal.lower() or "Budget envelope" in goal or "Time / budget" in goal
    assert "ROOT_CAUSE_CONFIRMED" in goal
    assert "fails before patch" in goal.lower() or "FAILS before" in goal or "fails before" in goal
    ledger = json.loads((exam / "MISSION_LEDGER.json").read_text(encoding="utf-8"))
    assert ledger["terminal_verdict"] == "ROOT_CAUSE_CONFIRMED"
    assert ledger["gos_modified"] is False
    assert ledger["hard_gate"]["regression_fail_before_pass_after"] is True
    root = (EXT / "EW2_oss_incident" / "ROOT_CAUSE.md").read_text(encoding="utf-8")
    assert "ROOT_CAUSE_CONFIRMED" in root
    assert (EXT / "EW2_oss_incident" / "proposed_fix.diff").is_file()
    before = (EXT / "EW2_oss_incident" / "repro" / "logs" / "regression_BEFORE_patch.txt").read_text(
        encoding="utf-8"
    )
    after = (EXT / "EW2_oss_incident" / "repro" / "logs" / "regression_AFTER_patch.txt").read_text(
        encoding="utf-8"
    )
    assert "FAILED" in before
    assert "2 passed" in after
    bottlenecks = (exam / "BOTTLENECKS.md").read_text(encoding="utf-8")
    assert "Intrinsic" in bottlenecks
    assert "Global OS" in bottlenecks
    ew1 = json.loads(
        (EXT / "EW1_transient_predictor" / "CURRENT_STATE.json").read_text(encoding="utf-8")
    )
    assert ew1["arms_started"] is False
