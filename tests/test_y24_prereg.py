"""Acceptance: Y24 prereg + prep locks + corpus seal + runner gates."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from global_os.evals.research.y24_arms import run_arm_stub
from global_os.evals.research.y24_complexity import assign_stratum, stratum_from_features
from global_os.evals.research.y24_cost import cost_match_ok, verification_cost
from global_os.evals.research.y24_gates import memory_pair_valid

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "y24"


def test_y24_prereg_locked() -> None:
    raw = json.loads((ART / "Y24-PREREG.json").read_text(encoding="utf-8"))
    st = json.loads((ART / "CURRENT_STATE.json").read_text(encoding="utf-8"))
    assert raw["status"] == "PREREG_LOCKED"
    assert st["t3_not_evidence"] is True
    assert st["trust_kernel_promoted"] is False
    assert raw["complexity_rubric"]["post_hoc_relabel_forbidden"] is True
    assert raw["isolation"][
        "arm_c_memory_builders_forbidden_sealed_access_before_unseal"
    ] is True


def test_y24_complexity_and_cost_helpers() -> None:
    assert assign_stratum(3) == "LOW"
    assert assign_stratum(4) == "MEDIUM"
    assert assign_stratum(7) == "HIGH"
    score, stratum = stratum_from_features(
        {"F_decomp": 2, "F_deps": 2, "F_vdepth": 2, "F_horizon": 1, "F_ext": 0}
    )
    assert score == 7 and stratum == "HIGH"
    ledger = {
        "llm_cost_tokens": 1000,
        "tool_calls": 2,
        "human_interventions": 0,
        "latency_ms": 1000,
        "verification_calls": 1,
        "recovery_overhead_seconds": 0,
    }
    assert verification_cost(ledger) == pytest.approx(1201.0)
    assert cost_match_ok(100.0, 125.0) is True


def test_y24_memory_pair_requires_unseen_variant() -> None:
    first = {
        "task_id": "t1",
        "failure_class": "auth_expand",
        "patch_ref": "p1",
        "memory_pair_id": "m1",
        "memory_role": "first",
    }
    variant = {
        "task_id": "t2",
        "failure_class": "auth_expand",
        "patch_ref": "p2",
        "memory_pair_id": "m1",
        "memory_role": "unseen_variant",
    }
    assert memory_pair_valid(first, variant) is True
    same = dict(first)
    same["memory_role"] = "unseen_variant"
    assert memory_pair_valid(first, same) is False


def test_y24_corpus_sealed_and_blind_public() -> None:
    man = json.loads((ART / "sealed" / "HOLDOUT_MANIFEST.json").read_text(encoding="utf-8"))
    assert man["status"] in {"FROZEN_UNSEEN", "UNSEALED_FOR_EXECUTION"}
    assert man["sha256_of_sealed_bundle"]
    assert (ART / "sealed" / "sealed_pack.json").is_file()
    blind = json.loads(
        (ART / "public" / "corpus_manifest.HOLDOUT_BLIND.json").read_text(encoding="utf-8")
    )
    for t in blind["tasks"]:
        assert "label" not in t
        assert "stratum" not in t
    report = json.loads((ART / "CORPUS_BUILD_REPORT.json").read_text(encoding="utf-8"))
    assert report["benign_suspicious_fraction_holdout"] >= 0.3 - 1e-9
    assert report["meets_min_12_per_stratum_combined"] is True
    assert report.get("holdout_min_per_stratum_met") is True
    hold_strata = report["holdout"]["strata"]
    assert hold_strata.get("MEDIUM", 0) >= 8
    assert hold_strata.get("HIGH", 0) >= 8
    assert man.get("fold") == "fold2_enlarged_holdout"


def test_y24_decision_artifact_present() -> None:
    decision = ART / "Y24_DECISION.md"
    score = ART / "SCORE_RAW.json"
    assert decision.is_file() and score.is_file()
    raw = json.loads(score.read_text(encoding="utf-8"))
    assert raw["decision"]["verdict"] in {"KEEP", "REJECT", "INCONCLUSIVE"}
    assert raw["t3_not_evidence"] is True
    assert raw["trust_kernel_promoted"] is False
    assert "Trust Kernel" in decision.read_text(encoding="utf-8")
    assert (ART / "Y24_EXPERIMENT_SHA.txt").is_file()
    assert "I did not access artifacts/y24/sealed" in (
        ART / "ISOLATION_ATTESTATION.md"
    ).read_text(encoding="utf-8")


def test_y24_naming_collision_documented() -> None:
    raw = json.loads((ART / "Y24-PREREG.json").read_text(encoding="utf-8"))
    assert raw["campaign_id"] == "Y24"
    assert "FROZEN" in (ROOT / "artifacts/y19/CLAIMS.md").read_text(encoding="utf-8")


def test_y24_stub_refuses_if_not_unsealed(monkeypatch: pytest.MonkeyPatch) -> None:
    # Temporarily pretend holdout frozen unseen
    man_path = ART / "sealed" / "HOLDOUT_MANIFEST.json"
    original = man_path.read_text(encoding="utf-8")
    data = json.loads(original)
    data["status"] = "FROZEN_UNSEEN"
    data["unsealed_for_execution"] = False
    man_path.write_text(json.dumps(data) + "\n", encoding="utf-8")
    try:
        with pytest.raises(RuntimeError, match="holdout not UNSEALED"):
            run_arm_stub("C", {"task_id": "x"})
    finally:
        man_path.write_text(original, encoding="utf-8")
