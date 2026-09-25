"""Acceptance tests for Y22 evidence A/B harness."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_y22_prereg_locked():
    assert (ROOT / "artifacts/y22/Y22-RESEARCH-PROGRAM.md").is_file()
    assert (ROOT / "artifacts/y22/Y22-PREREG.md").is_file()
    state = json.loads((ROOT / "artifacts/y22/CURRENT_STATE.json").read_text(encoding="utf-8"))
    assert state["protocol_version"] == "Y22-AB-v1"
    assert state["prereg_locked"] is True
    assert state["arms_started"] is False or state["arms"]["A"]["status"] in {
        "NOT_STARTED",
        "RUNNING",
        "FROZEN",
        "FROZEN_SCORED",
    }
    assert state["win_primary"] == "reliability_composite"
    assert state["primary_mcid"] == 0.05
    assert abs(sum(state["weights"].values()) - 1.0) < 1e-9
    assert state.get("public_pack_sha256")
    # Mechanism hypothesis lives on public pack / prereg; scored CURRENT_STATE may omit it.
    public = json.loads((ROOT / "artifacts/y22/public/public_pack.json").read_text(encoding="utf-8"))
    assert "mechanism_hypothesis" in public
    assert state.get("gos_advantage_claimed") is False


def test_y22_public_hides_truth_and_scoring(tmp_path: Path):
    from global_os.evals.research.y22_evidence_ab import (
        WEIGHTS,
        build_public_pack,
        build_sealed_pack,
        compare_primary,
        export_packs,
        public_pack_leaks_secrets,
        score_submission,
    )

    public = build_public_pack()
    assert public_pack_leaks_secrets(public) == []
    assert "events" in public and "questions" in public
    sealed = build_sealed_pack()
    # Perfect: all answers correct, invalidate all must, active only true, drop interim
    perfect = {
        "arm_id": "T",
        "final_answers": [
            {"question_id": q["question_id"], "value": q["answer"]} for q in sealed["questions"]
        ],
        "active_claims": list(sealed["allowed_true_fact_ids"])[:5],
        "invalidated_claims": list(sealed["must_invalidate"]),
        "dropped_interim": True,
        "decision": "SUPPORTED",
    }
    s = score_submission(perfect, sealed)
    assert s["composite"] > 0.85
    empty = {
        "final_answers": [],
        "active_claims": list(sealed["must_invalidate"]),
        "invalidated_claims": [],
        "dropped_interim": False,
        "decision": "INCONCLUSIVE",
    }
    s0 = score_submission(empty, sealed)
    assert s0["composite"] < s["composite"]
    assert compare_primary(s0, s)["verdict"] == "B_WINS_PRIMARY"
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9
    hashes = export_packs(public_dir=tmp_path / "p", sealed_dir=tmp_path / "s")
    assert len(hashes["public_pack_sha256"]) == 64
