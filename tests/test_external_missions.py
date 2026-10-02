"""Acceptance: external missions + M-EXT1/M-EXT2 terminals + M-EXT3 prereg."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "artifacts" / "external"


def test_external_contract_locked() -> None:
    raw = json.loads((EXT / "CONTRACT" / "EXTERNAL_REAL_WORK.json").read_text(encoding="utf-8"))
    assert raw["status"] == "CONTRACT_LOCKED"
    assert "EW1" in raw["missions"] and "EW2" in raw["missions"]
    assert "M-EXT3-GSA" in raw["missions"]
    assert "M-EXT4-MPEMBA" in raw["missions"]
    assert "M-EXT5-INIT-MPEMBA" in raw["missions"]


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


def test_m_ext3_closed_tie_both_hard_gates() -> None:
    exam = EXT / "M_EXT3_GOS_VS_AGENT"
    closed = json.loads((exam / "M_EXT3_CLOSED.json").read_text(encoding="utf-8"))
    assert closed["status"] == "CAMPAIGN_CLOSED"
    assert closed["terminal"] == "TIE"
    assert closed["HG_A"] == 1 and closed["HG_B"] == 1
    assert closed["h_gsa_primary_advantage"] == "NOT_CONFIRMED"
    assert closed["architecture_changes"] == "NONE"
    score = json.loads((exam / "SCORE_RAW.json").read_text(encoding="utf-8"))
    assert score["primary_verdict"] == "TIE"
    assert score["integrity"]["gos_architecture_changed"] is False
    pin = json.loads((exam / "TASK_PIN.json").read_text(encoding="utf-8"))
    assert pin["issue_number"] == 3614
    assert pin["repo"] == "encode/httpx"
    assert pin["contaminates_m_ext1"] is False
    for arm in ("A", "B"):
        sub = json.loads((exam / "arms" / arm / "submission.json").read_text(encoding="utf-8"))
        assert sub["HG"] == 1
        assert sub["terminal"] == "ROOT_CAUSE_CONFIRMED"
        assert all(sub["hard_gate"].values())
        before = (exam / "arms" / arm / "workdir" / "repro" / "logs" / "regression_BEFORE_patch.txt").read_text(
            encoding="utf-8"
        )
        after = (exam / "arms" / arm / "workdir" / "repro" / "logs" / "regression_AFTER_patch.txt").read_text(
            encoding="utf-8"
        )
        assert "FAILED" in before
        assert "2 passed" in after or "0 failed" in after
    assert "TIE" in (exam / "COMPARISON_REPORT.md").read_text(encoding="utf-8")
    prereg = json.loads((exam / "M-EXT3-PREREG.json").read_text(encoding="utf-8"))
    assert prereg["secondary_cannot_override_primary_for_B_ADVANTAGE"] is True


def test_m_ext1_still_immutable_under_m_ext3() -> None:
    closed = json.loads((EXT / "M_EXT1_EW2_EXAM" / "M_EXT1_CLOSED.json").read_text(encoding="utf-8"))
    assert closed["status"] == "IMMUTABLE_TERMINAL"
    assert closed["gos_self_score_polish_forbidden"] is True


def test_m_ext4_terminal_with_post_hoc_audit() -> None:
    exam = EXT / "M_EXT4_MPEMBA_EXAM"
    # Agent historical terminal remains
    decision = (exam / "DECISION.md").read_text(encoding="utf-8")
    assert "NOT_NOVEL_IN_CLAIMED_FORM" in decision
    assert "ILL_POSED" in decision
    # Audit layer corrects accumulated claim without rewriting DECISION meaning as sole headline
    audit = (exam / "POST_HOC_AUDIT.md").read_text(encoding="utf-8")
    assert "SUCCESSFUL SCIENTIFIC TRIAGE" in audit
    assert "UNRESOLVED" in audit
    assert "NOT TESTED" in audit
    errata = (exam / "ERRATA.md").read_text(encoding="utf-8")
    assert "14/20" in errata or "P(X" in errata
    assert "confirmatory" in errata.lower()
    claim = (exam / "ACCUMULATED_CLAIM.md").read_text(encoding="utf-8")
    assert "SUCCESSFUL SCIENTIFIC TRIAGE" in claim
    assert "UNRESOLVED" in claim
    assert "NOT TESTED" in claim
    ledger = json.loads((exam / "MISSION_LEDGER.json").read_text(encoding="utf-8"))
    assert ledger["source_hypothesis_immutable"] is True
    assert ledger["decision"] == "NOT_NOVEL_IN_CLAIMED_FORM"
    assert ledger["exam_outcome_post_audit"] == "SUCCESSFUL_SCIENTIFIC_TRIAGE"
    assert ledger["empirical_post_audit"] == "NOT_TESTED"
    # Confirmatory CLI is not actually implemented (errata F5/E5)
    code = (EXT / "EW4_mpemba_nn" / "code" / "mpemba_experiment.py").read_text(encoding="utf-8")
    assert "sys.exit(1)" in code
    assert "--confirmatory" in code


def test_m_ext5_mission_open_gate_pending() -> None:
    exam = EXT / "M_EXT5_INIT_MPEMBA_EXAM"
    gate = json.loads((exam / "M-EXT5-PREREG-GATE.json").read_text(encoding="utf-8"))
    assert gate["status"] == "MISSION_OPEN"
    assert gate["science_cycle_started"] is False
    assert gate["mechanical_gate_required"] is True
    assert "H_EFFECT" in gate["hypotheses"] and "H_FISHER" in gate["hypotheses"]
    assert "reuse_m_ext4_14_of_20_broken_alpha_rule" in gate["forbidden"]
    ledger = json.loads((exam / "MISSION_LEDGER.json").read_text(encoding="utf-8"))
    assert ledger["mechanical_gate_status"] == "ALL_PENDING"
    assert ledger["phases"]["B_mechanical_gate"] == "PENDING"
    assert not (exam / "DECISION.md").exists()
    mech = (exam / "MECHANICAL_GATE.md").read_text(encoding="utf-8")
    assert "PENDING" in mech
    assert "GATE_OPEN_ALL_PENDING" in mech
    hy = (exam / "HYPOTHESES.md").read_text(encoding="utf-8")
    assert "H_EFFECT" in hy and "H_FISHER" in hy
    assert "Observing crossing" in hy or "crossing" in hy.lower()
