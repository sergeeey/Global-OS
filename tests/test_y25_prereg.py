"""Acceptance: Y25 Memory Value prereg locks + corpus seal + decision boundary."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from global_os.evals.research.y25_arms import run_arm_stub
from global_os.evals.research.y25_cost import memory_cost_ratio_ok, pair_cost
from global_os.evals.research.y25_gates import memory_pair_valid

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "y25"
Y24 = ROOT / "artifacts" / "y24"


def test_y25_prereg_frozen_before_corpus() -> None:
    raw = json.loads((ART / "Y25-PREREG.json").read_text(encoding="utf-8"))
    freeze = json.loads((ART / "Y25_PREREG_FREEZE.json").read_text(encoding="utf-8"))
    closed = json.loads((Y24 / "Y24_CLOSED.json").read_text(encoding="utf-8"))
    y25c = json.loads((ART / "Y25_CLOSED.json").read_text(encoding="utf-8"))
    assert raw["status"] == "PREREG_LOCKED"
    assert raw["protocol_id"] == "Y25-MV-v1"
    assert freeze["status"] == "PREREG_SHA_FROZEN"
    assert (ART / "Y25_PREREG_SHA.txt").read_text(encoding="utf-8").strip()
    assert freeze["sample_size_expansion_after_unseal"] == (
        "FORBIDDEN_WITHOUT_LOCKED_AMENDMENT"
    )
    assert closed["status"] == "CAMPAIGN_CLOSED"
    assert closed["post_hoc_y24_rescue_forbidden"] is True
    assert y25c["status"] == "CAMPAIGN_CLOSED"
    assert y25c["decision"] == "REJECT"
    assert y25c["memory_value"] == "NOT_SHOWN_AT_PREREGISTERED_STRENGTH"
    assert y25c["y25_f2"] == "FORBIDDEN_NOW"
    assert "EXTERNAL_REAL_WORK" in y25c["next"]
    assert "Y25-F2" in (ART / "Y25_CLOSED.md").read_text(encoding="utf-8")
    assert (ROOT / "artifacts" / "NEXT_EXTERNAL_REAL_WORK.md").is_file()


def test_y25_cost_and_memory_ratio() -> None:
    ledger = {
        "llm_cost_tokens": 100,
        "tool_calls": 2,
        "human_interventions": 0,
        "latency_ms": 1000,
        "verification_calls": 1,
        "recovery_overhead_seconds": 0,
        "time_to_diagnosis_s": 30,
    }
    assert pair_cost(ledger) == pytest.approx(331.0)
    assert memory_cost_ratio_ok(100.0, 60.0) is True
    assert memory_cost_ratio_ok(100.0, 61.0) is False


def test_y25_unseen_variant_gate() -> None:
    first = {
        "task_id": "a",
        "failure_class": "path_traversal",
        "repo_url": "https://github.com/org/r1",
        "commit_sha": "aaa",
        "patch_ref": "p1",
        "memory_role": "first",
    }
    variant = {
        "task_id": "b",
        "failure_class": "path_traversal",
        "repo_url": "https://github.com/org/r2",
        "commit_sha": "bbb",
        "patch_ref": "p2",
        "memory_role": "unseen_variant",
    }
    assert memory_pair_valid(first, variant) is True
    same = dict(first)
    same["memory_role"] = "unseen_variant"
    assert memory_pair_valid(first, same) is False


def test_y25_corpus_sealed_and_scored() -> None:
    report = json.loads((ART / "CORPUS_BUILD_REPORT.json").read_text(encoding="utf-8"))
    man = json.loads((ART / "sealed" / "HOLDOUT_MANIFEST.json").read_text(encoding="utf-8"))
    assert report["n_pairs_total"] >= 12
    assert report["holdout"]["n_pairs"] >= 12
    assert man["status"] in {"FROZEN_UNSEEN", "UNSEALED_FOR_EXECUTION"}
    assert man["sha256_of_sealed_bundle"]
    blind = json.loads(
        (ART / "public" / "corpus_manifest.HOLDOUT_BLIND.json").read_text(encoding="utf-8")
    )
    for p in blind["pairs"]:
        assert "failure_class" not in p
    score = json.loads((ART / "SCORE_RAW.json").read_text(encoding="utf-8"))
    assert score["decision"]["verdict"] in {"KEEP", "REJECT", "INCONCLUSIVE"}
    assert score["y24_not_rescued"] is True
    assert score["trust_kernel_promoted"] is False
    assert "Trust Kernel" in (ART / "Y25_DECISION.md").read_text(encoding="utf-8")
    assert "I did not access artifacts/y25/sealed" in (
        ART / "ISOLATION_ATTESTATION.md"
    ).read_text(encoding="utf-8")


def test_y25_stub_refuses_if_frozen_unseen(monkeypatch: pytest.MonkeyPatch) -> None:
    man_path = ART / "sealed" / "HOLDOUT_MANIFEST.json"
    original = man_path.read_text(encoding="utf-8")
    data = json.loads(original)
    data["status"] = "FROZEN_UNSEEN"
    data["unsealed_for_execution"] = False
    man_path.write_text(json.dumps(data) + "\n", encoding="utf-8")
    try:
        with pytest.raises(RuntimeError, match="holdout not UNSEALED"):
            run_arm_stub("W1", {"task_id": "x"})
    finally:
        man_path.write_text(original, encoding="utf-8")
