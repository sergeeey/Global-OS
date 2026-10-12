"""Acceptance: PhaseBreak pilot pack is self-consistent (PILOT-PB-CLAIMS-v1)."""

from __future__ import annotations

import json
from pathlib import Path

PACK = Path("artifacts/pilot/phasebreak")


def test_pilot_pack_files_exist() -> None:
    for name in (
        "GOAL_CONTRACT.md",
        "CLAIM_LEDGER.json",
        "VERIFIED_NUMBERS.json",
        "DECISION.md",
        "INTERVENTIONS.json",
        "README.md",
        "EFFECT_RECEIPT.md",
        "CODEX_FOLLOWUPS.md",
    ):
        assert (PACK / name).is_file(), name


def test_effect_receipt_reconciled() -> None:
    text = (PACK / "EFFECT_RECEIPT.md").read_text(encoding="utf-8")
    assert "RECONCILED" in text
    assert "0161463" in text
    assert "PhaseBreak-2026/pull/1" in text


def test_verified_finance_matches_ledger_support() -> None:
    nums = json.loads((PACK / "VERIFIED_NUMBERS.json").read_text(encoding="utf-8"))
    ledger = json.loads((PACK / "CLAIM_LEDGER.json").read_text(encoding="utf-8"))
    fin = nums["domains"]["finance"]
    assert abs(fin["precision"] - 0.778) < 1e-3
    assert abs(fin["recall"] - 0.636) < 1e-3
    c01 = next(c for c in ledger["claims"] if c["id"] == "C01")
    assert c01["verdict"] == "SUPPORTED"


def test_commodities_readme_stale_flagged() -> None:
    nums = json.loads((PACK / "VERIFIED_NUMBERS.json").read_text(encoding="utf-8"))
    ledger = json.loads((PACK / "CLAIM_LEDGER.json").read_text(encoding="utf-8"))
    assert nums["readme_vs_json"]["commodities_recall_match"] is False
    c03 = next(c for c in ledger["claims"] if c["id"] == "C03")
    assert c03["verdict"] == "REJECTED"


def test_production_usable_rejected() -> None:
    ledger = json.loads((PACK / "CLAIM_LEDGER.json").read_text(encoding="utf-8"))
    c11 = next(c for c in ledger["claims"] if c["id"] == "C11")
    assert c11["verdict"] == "REJECTED"
    crash = json.loads((PACK / "VERIFIED_NUMBERS.json").read_text(encoding="utf-8"))[
        "crash_eval"
    ]
    assert crash["crash_precision"] == 0.5
    assert crash["crash_recall"] < 0.25


def test_decision_mentions_terminal_and_no_gos_advantage() -> None:
    text = (PACK / "DECISION.md").read_text(encoding="utf-8")
    assert "REJECTED" in text
    assert "NOT_MEASURED" in text or "not measured" in text.lower()
