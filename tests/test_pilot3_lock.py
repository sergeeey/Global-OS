"""Acceptance: Pilot 3 lock is coherent and arms not started at lock commit."""

from __future__ import annotations

import json
from pathlib import Path

PACK = Path("artifacts/pilot/pilot3_independent")


def test_pilot3_locked_on_paperclip() -> None:
    lock = json.loads((PACK / "LOCK.json").read_text(encoding="utf-8"))
    # Lock commit had status LOCKED; after arm start status advances to RUNNING/TERMINAL.
    assert lock["status"] in {"LOCKED", "RUNNING", "EVAL_SEALED", "TERMINAL"}
    assert lock["target"]["full_name"] == "sergeeey/Paperclip-AI---2026"
    assert lock["target"]["pin_sha"].startswith("47c232b")
    assert lock["decisive_comparison"] == "C_vs_B"
    assert lock["provider_budget_pins"]["fidelity"] == "ISOLATED_SUBAGENT_ARMS_SAME_ORCHESTRATOR"
    assert lock["ablation_checklist_sha256"]
    assert (PACK / "TASK_BRIEF.md").is_file()
    assert (PACK / "TARGET_SELECTION.md").is_file()
    for arm in "ABCD":
        assert (PACK / "arms" / f"PROTOCOL_{arm}.md").is_file()
    assert "SELECTED" in (PACK / "TARGET_SELECTION.md").read_text(encoding="utf-8")
    assert "contamination" in (PACK / "TARGET_SELECTION.md").read_text(encoding="utf-8").lower()
    if lock["status"] == "LOCKED":
        assert lock["arms_started"] is False
    else:
        assert lock["arms_started"] is True
