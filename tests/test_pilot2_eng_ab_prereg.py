"""Acceptance: Pilot 2 eng A/B prereg pack is present and coherent."""

from __future__ import annotations

from pathlib import Path

PACK = Path("artifacts/pilot/pilot2_eng_ab")


def test_pilot2_prereg_files_exist() -> None:
    for name in (
        "README.md",
        "GOAL_CONTRACT.md",
        "PREREG.md",
        "FINDING_RUBRIC.md",
        "METRICS.md",
        "TARGET_SELECTION.md",
        "LOCK_CHECKLIST.md",
        "PHASEBREAK_HYGIENE_HANDOFF.md",
    ):
        assert (PACK / name).is_file(), name


def test_hypothesis_and_ordered_eval_present() -> None:
    goal = (PACK / "GOAL_CONTRACT.md").read_text(encoding="utf-8")
    prereg = (PACK / "PREREG.md").read_text(encoding="utf-8")
    assert "H-PILOT2-001" in goal
    assert "PREREG_DRAFT" in goal or "DRAFT" in prereg
    assert "No critical invariant regression" in prereg
    assert "Global-OS" in (PACK / "TARGET_SELECTION.md").read_text(encoding="utf-8")


def test_finding_rubric_rejects_vague_claims() -> None:
    text = (PACK / "FINDING_RUBRIC.md").read_text(encoding="utf-8")
    assert "race condition possible" in text
    assert "independently checked" in text
