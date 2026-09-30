"""Acceptance: Y24 prereg locked before arms / holdout unseal."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "y24"


def test_y24_prereg_locked_and_arms_not_started() -> None:
    md = ART / "Y24-PREREG.md"
    js = ART / "Y24-PREREG.json"
    prog = ART / "Y24-RESEARCH-PROGRAM.md"
    state = ART / "CURRENT_STATE.json"
    assert md.is_file() and js.is_file() and prog.is_file() and state.is_file()

    raw = json.loads(js.read_text(encoding="utf-8"))
    st = json.loads(state.read_text(encoding="utf-8"))
    assert raw["status"] == "PREREG_LOCKED"
    assert raw["arms_started"] is False
    assert raw["holdout_status"] == "NOT_SEALED_YET"
    assert st["phase"] == "PREREG_LOCKED"
    assert st["arms_started"] is False
    assert st["t3_not_evidence"] is True
    assert st["trust_kernel_promoted"] is False
    assert st["c2_edited"] is False


def test_y24_arms_metrics_and_decision_surface() -> None:
    raw = json.loads((ART / "Y24-PREREG.json").read_text(encoding="utf-8"))
    assert set(raw["arms"]) == {"A", "B", "C"}
    assert "benign_suspicious" in raw["task_labels"]
    assert raw["benign_suspicious_min_fraction_of_benign"] >= 0.3
    assert set(raw["complexity_strata"]) == {"LOW", "MEDIUM", "HIGH"}
    for m in (
        "material_escape_rate",
        "false_block_rate",
        "task_completion_rate",
        "verification_cost",
    ):
        assert m in raw["metrics"]
    assert "MEDIUM" in raw["decision"]["keep_requires_stratum"]
    assert "HIGH" in raw["decision"]["keep_requires_stratum"]
    assert raw["y23_forbidden"] is True
    assert raw["legacy_y19_status"] == "FROZEN_DO_NOT_REOPEN"
    forb = set(raw["forbidden"])
    assert "use_t3_keep_as_y24_evidence" in forb
    assert "trust_kernel_promote_from_y24_alone" in forb
    assert "edit_c2_selective_bounded_recovery_for_y24" in forb


def test_y24_does_not_reopen_legacy_y19() -> None:
    prog = (ART / "Y24-RESEARCH-PROGRAM.md").read_text(encoding="utf-8")
    assert "FROZEN" in prog
    assert "Y24" in prog
    claims = (ART / "CLAIMS.md").read_text(encoding="utf-8")
    assert "not T3 overturn" in claims or "not T3" in claims
    # sealed dir must not yet contain labeled holdout pack
    sealed = ART / "sealed"
    assert sealed.is_dir()
    assert not (sealed / "holdout_labels.json").exists()
    assert not (sealed / "sealed_pack.json").exists()


def test_y24_naming_collision_documented() -> None:
    """Informal brief said Y19; repo Y19 is frozen — campaign id must be Y24."""
    raw = json.loads((ART / "Y24-PREREG.json").read_text(encoding="utf-8"))
    assert raw["campaign_id"] == "Y24"
    assert raw["informal_brief_name"] == "Y19_adaptive_verifier_threshold"
    legacy = ROOT / "artifacts" / "y19" / "CLAIMS.md"
    assert legacy.is_file()
    text = legacy.read_text(encoding="utf-8")
    assert "FROZEN" in text
