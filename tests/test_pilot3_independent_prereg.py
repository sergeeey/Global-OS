"""Acceptance: Pilot 3 independent eng validation prereg pack is coherent."""

from __future__ import annotations

import json
from pathlib import Path

PACK = Path("artifacts/pilot/pilot3_independent")
FIX = Path("artifacts/pilot/mcp_bouncer_fix")


def test_pilot3_prereg_files_exist() -> None:
    for name in (
        "README.md",
        "GOAL_CONTRACT.md",
        "PREREG.md",
        "ABLATION.md",
        "FIDELITY.md",
        "FINDING_RUBRIC.md",
        "METRICS.md",
        "LOCK_CHECKLIST.md",
        "LOCK.json",
        "RUN_STATE.md",
    ):
        assert (PACK / name).is_file(), name


def test_pilot3_arms_abcd_and_decisive_c_vs_b() -> None:
    goal = (PACK / "GOAL_CONTRACT.md").read_text(encoding="utf-8")
    prereg = (PACK / "PREREG.md").read_text(encoding="utf-8")
    ablation = (PACK / "ABLATION.md").read_text(encoding="utf-8")
    fidelity = (PACK / "FIDELITY.md").read_text(encoding="utf-8")
    assert "H-PILOT3-EPI" in goal
    assert "H-PILOT3-ENG" in goal
    assert "H-PILOT3-EFF" in goal
    assert "H-PILOT3-ATTR" in goal
    assert "C vs B" in goal or "C vs B" in prereg
    assert "INDEPENDENT_EXECUTORS_PLUS_ABLATION" in prereg or "independent" in prereg.lower()
    assert "SAME_EXECUTOR_DUAL_PROTOCOL" in fidelity
    assert "Arm id:** `B`" in ablation or "Arm id: `B`" in ablation
    assert "Epistemic Kernel" in ablation
    assert "evaluator d" in (prereg + fidelity).lower() or "| D |" in fidelity or "D blind" in fidelity
    assert "blind" in prereg.lower()


def test_pilot3_lock_shape_and_arms() -> None:
    lock = json.loads((PACK / "LOCK.json").read_text(encoding="utf-8"))
    assert lock["status"] in {"PREREG_DRAFT", "LOCKED", "RUNNING", "TERMINAL"}
    assert set(lock["hypotheses"]) == {"H-PILOT3-EPI", "H-PILOT3-ENG", "H-PILOT3-EFF"}
    assert lock["attribution_hypothesis"] == "H-PILOT3-ATTR"
    assert lock["decisive_comparison"] == "C_vs_B"
    assert lock["arms"]["A"] == "strong_single_agent"
    assert "disciplined" in lock["arms"]["B"]
    assert "global_os" in lock["arms"]["C"]
    assert lock["arms"]["D"] == "blind_evaluator"
    assert "E" not in lock["arms"]


def test_pilot3_forbids_self_certification() -> None:
    prereg = (PACK / "PREREG.md").read_text(encoding="utf-8")
    assert "self-certification" in prereg
    assert "No M2" in (PACK / "GOAL_CONTRACT.md").read_text(encoding="utf-8") or "No M2" in prereg


def test_mcp_bouncer_fix_reconciled_and_ci_verified() -> None:
    assert (FIX / "mcp-bouncer-pilot2-sealed-fixes.patch").is_file()
    assert (FIX / "mcp-bouncer-ci-ruff-fix.patch").is_file()
    receipt = (FIX / "EFFECT_RECEIPT.md").read_text(encoding="utf-8")
    assert "RECONCILED" in receipt
    assert "CI_VERIFIED" in receipt
    assert "33030e3" in receipt
    assert "6ccce71" in receipt
    assert "38261957403" in receipt
    handoff = (FIX / "HANDOFF.md").read_text(encoding="utf-8")
    assert "CI_VERIFIED" in handoff
    assert "CLOSED" in handoff
