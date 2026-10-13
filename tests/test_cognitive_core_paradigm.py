"""Guards for Cognitive Core paradigm + Challenge lock pointer."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "artifacts" / "pilot" / "cognitive_core"
CHAL = ROOT / "artifacts" / "pilot" / "challenge_ga"


def test_paradigm_locks_achiever_over_platform_only():
    text = (PACK / "PARADIGM.md").read_text(encoding="utf-8")
    assert "Autonomous Goal Achiever" in text
    assert "inescapable core" in text or "Reliability substrate" in text
    assert "Forbidden swap" in text
    assert "NOT_SHOWN" in text
    assert "M2" in text or "reopening M2" in text
    assert "stop micro-reproving" in text or "stop:" in text


def test_organs_and_challenge_lock_present():
    organs = (PACK / "COGNITIVE_ORGANS.md").read_text(encoding="utf-8")
    draft = (PACK / "CHALLENGE_CONTRACT_DRAFT.md").read_text(encoding="utf-8")
    assert "CONTRACTS_LOCKED" in organs
    assert "Decomposer" in organs
    assert "Pivot" in organs
    assert "Orchestration" in organs
    assert "ADR-0009" in organs
    assert "PREREG_LOCKED" in draft or (CHAL / "LOCK.json").is_file()
    assert "H-GA-ATTR" in draft or "H-GA-ATTR" in (CHAL / "CHALLENGE_GA_CONTRACT.md").read_text(
        encoding="utf-8"
    )
    assert (CHAL / "LOCK.json").is_file()
    assert "Terminal goal criterion" in (CHAL / "CHALLENGE_GA_CONTRACT.md").read_text(
        encoding="utf-8"
    )
    assert "Stop conditions" in (CHAL / "CHALLENGE_GA_CONTRACT.md").read_text(encoding="utf-8")


def test_roadmap_points_to_cognitive_core():
    roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
    assert "cognitive_core" in roadmap or "Cognitive Core" in roadmap
    assert "Autonomous" in roadmap
    assert "Challenge-GA" in roadmap or "CHALLENGE-GA" in roadmap
