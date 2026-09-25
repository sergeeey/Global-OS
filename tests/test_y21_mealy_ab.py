"""Acceptance tests for Y21 Mealy A/B harness (prereg stage)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_y21_prereg_files_and_state():
    assert (ROOT / "artifacts/y21/Y21-RESEARCH-PROGRAM.md").is_file()
    assert (ROOT / "artifacts/y21/Y21-PREREG.md").is_file()
    state = json.loads((ROOT / "artifacts/y21/CURRENT_STATE.json").read_text(encoding="utf-8"))
    assert state["protocol_version"] == "Y21-AB-v1"
    assert state["prereg_locked"] is True
    assert state["arms_started"] is False or state["arms"]["A"]["status"] in {
        "NOT_STARTED",
        "RUNNING",
        "FROZEN",
    }
    assert state["win_primary"] == "sealed_exact_match_rate"
    assert state["primary_mcid"] == 0.05
    assert state.get("public_pack_sha256")
    assert state.get("sealed_pack_sha256")
    assert state.get("generator_module_sha256")


def test_public_hides_mealy_and_scoring(tmp_path: Path):
    from global_os.evals.research.y21_mealy_ab import (
        PRIMARY_MCID,
        build_public_pack,
        build_sealed_pack,
        compare_primary,
        export_packs,
        public_pack_leaks_secrets,
        score_submission,
    )

    public = build_public_pack()
    assert public_pack_leaks_secrets(public) == []
    assert "train_traces" in public and "predict_inputs" in public
    sealed = build_sealed_pack()
    # perfect
    perfect = {
        "arm_id": "T",
        "predicted_outputs": [
            {"trace_id": t["trace_id"], "output": t["output"]} for t in sealed["sealed_traces"]
        ],
        "decision": "SUPPORTED",
    }
    s = score_submission(perfect, sealed)
    assert s["sealed_exact_match_rate"] == 1.0
    empty = {"predicted_outputs": [], "decision": "INCONCLUSIVE"}
    s0 = score_submission(empty, sealed)
    assert s0["sealed_exact_match_rate"] == 0.0
    cmp_ = compare_primary(s0, s)
    assert cmp_["verdict"] == "B_WINS_PRIMARY"
    assert PRIMARY_MCID == 0.05
    hashes = export_packs(public_dir=tmp_path / "p", sealed_dir=tmp_path / "s")
    assert len(hashes["public_pack_sha256"]) == 64
