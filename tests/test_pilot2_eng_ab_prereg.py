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
        "LOCK.json",
    ):
        assert (PACK / name).is_file(), name


def test_hypothesis_and_ordered_eval_present() -> None:
    goal = (PACK / "GOAL_CONTRACT.md").read_text(encoding="utf-8")
    prereg = (PACK / "PREREG.md").read_text(encoding="utf-8")
    assert "H-PILOT2-001" in goal
    assert "TARGET_LOCKED" in goal or "TARGET_LOCKED" in prereg
    assert "No critical invariant regression" in prereg
    assert "Global-OS" in (PACK / "TARGET_SELECTION.md").read_text(encoding="utf-8")


def test_mcp_bouncer_target_locked() -> None:
    import json

    lock = json.loads((PACK / "LOCK.json").read_text(encoding="utf-8"))
    assert lock["status"] in {"TARGET_LOCKED", "ARMS_COMPLETE"}
    assert lock["target"]["full_name"] == "sergeeey/mcp-bouncer"
    assert lock["target"]["pin_sha"].startswith("45af092")
    assert "mcp-bouncer" in (PACK / "TARGET_SELECTION.md").read_text(encoding="utf-8")


def test_pilot2_decision_terminal() -> None:
    import json

    decision = (PACK / "DECISION.md").read_text(encoding="utf-8")
    assert "PARTIAL_SUPPORT_PROCESS_ONLY" in decision
    assert "NOT_SHOWN" in decision
    score = json.loads((PACK / "score/SCOREBOARD.json").read_text(encoding="utf-8"))
    assert score["fidelity"] == "SAME_EXECUTOR_DUAL_PROTOCOL"
    assert (PACK / "repro/PYTEST_OUT.txt").is_file()
    assert "7 failed" in (PACK / "repro/PYTEST_OUT.txt").read_text(encoding="utf-8")
    assert (PACK / "arms/FIDELITY.md").is_file()


def test_finding_rubric_rejects_vague_claims() -> None:
    text = (PACK / "FINDING_RUBRIC.md").read_text(encoding="utf-8")
    assert "race condition possible" in text
    assert "independently checked" in text
