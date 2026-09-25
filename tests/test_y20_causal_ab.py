"""Acceptance tests for Y20 preregistered causal A/B harness."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_y20_program_and_prereg_locked():
    prog = ROOT / "artifacts" / "y20" / "Y20-RESEARCH-PROGRAM.md"
    prereg = ROOT / "artifacts" / "y20" / "Y20-PREREG.md"
    state = ROOT / "artifacts" / "y20" / "CURRENT_STATE.json"
    claims = ROOT / "artifacts" / "y19" / "CLAIMS.md"
    evidence = ROOT / "artifacts" / "y19" / "EVIDENCE_PACK.md"
    assert prog.is_file()
    assert prereg.is_file()
    assert state.is_file()
    assert claims.is_file()
    assert evidence.is_file()
    payload = json.loads(state.read_text(encoding="utf-8"))
    assert payload["phase"] == "PREREG_LOCKED"
    assert payload["arms_started"] is False
    assert payload["gos_advantage_claimed"] is False
    assert payload["arms"]["A"]["status"] == "NOT_STARTED"
    assert payload["arms"]["B"]["status"] == "NOT_STARTED"
    assert payload["arms"]["C"]["status"] == "DEFERRED"
    text = claims.read_text(encoding="utf-8")
    assert "NOT PROVEN" in text
    assert "bundle" in text.lower() or "связки" in text.lower() or "model + Global OS" in text


def test_public_pack_hides_ground_truth(tmp_path: Path):
    from global_os.evals.research.y20_causal_ab import (
        BUDGETS,
        PROTOCOL_VERSION,
        build_public_pack,
        build_sealed_pack,
        export_packs,
        public_pack_leaks_secrets,
        score_submission,
        validate_budget_usage,
    )

    public = build_public_pack()
    assert public["protocol_version"] == PROTOCOL_VERSION
    assert public_pack_leaks_secrets(public) == []
    assert "rows" in public and len(public["rows"]) >= 1000
    assert len(public["variables"]) == 20

    sealed = build_sealed_pack()
    assert sealed["scoring_edges"]
    assert sealed["intervention_truth"]

    # Perfect submission should score well
    perfect = {
        "arm_id": "TEST",
        "claimed_edges": [list(e) for e in sealed["scoring_edges"]],
        "intervention_predictions": [
            {
                "intervention_id": t["intervention_id"],
                "target": t["target"],
                "predicted_mean": t["true_mean"],
            }
            for t in sealed["intervention_truth"]
        ],
        "decision": "SUPPORTED",
    }
    metrics = score_submission(perfect, sealed)
    assert metrics["edge_precision"] == 1.0
    assert metrics["edge_recall"] == 1.0
    assert metrics["intervention_mae"] is not None
    assert metrics["intervention_mae"] < 1e-9

    # Empty claims → low recall
    empty = {
        "claimed_edges": [],
        "intervention_predictions": [],
        "decision": "INCONCLUSIVE",
    }
    bad = score_submission(empty, sealed)
    assert bad["edge_recall"] == 0.0
    assert bad["intervention_missing"] >= 1

    pub_dir = tmp_path / "public"
    seal_dir = tmp_path / "sealed"
    hashes = export_packs(public_dir=pub_dir, sealed_dir=seal_dir)
    assert len(hashes["public_pack_sha256"]) == 64
    assert len(hashes["sealed_pack_sha256"]) == 64
    assert (pub_dir / "observational.csv").is_file()
    assert (seal_dir / "world.json").is_file()
    # public meta must not embed true means
    meta = json.loads((pub_dir / "public_meta.json").read_text(encoding="utf-8"))
    assert "true_mean" not in json.dumps(meta)

    assert BUDGETS["wall_seconds_max"] == 14400
    ok = validate_budget_usage(
        {
            "wall_seconds_used": 100,
            "token_budget_used": 1000,
            "tool_calls_used": 10,
            "python_subprocess_used": 5,
        }
    )
    assert ok["ok"] is True
    over = validate_budget_usage({"wall_seconds_used": 999999, "token_budget_used": 1, "tool_calls_used": 1, "python_subprocess_used": 1})
    assert over["ok"] is False


def test_export_packs_deterministic(tmp_path: Path):
    from global_os.evals.research.y20_causal_ab import export_packs

    a = export_packs(public_dir=tmp_path / "a_pub", sealed_dir=tmp_path / "a_seal")
    b = export_packs(public_dir=tmp_path / "b_pub", sealed_dir=tmp_path / "b_seal")
    assert a["public_pack_sha256"] == b["public_pack_sha256"]
    assert a["sealed_pack_sha256"] == b["sealed_pack_sha256"]


def test_y19_still_frozen():
    state = json.loads(
        (ROOT / "artifacts" / "y19" / "CURRENT_STATE.json").read_text(encoding="utf-8")
    )
    assert state.get("frozen") is True
    assert state.get("stop_reason") == "terminal_scientific_result"
