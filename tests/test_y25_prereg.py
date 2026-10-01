"""Acceptance: Y25 Memory Value prereg locks + Y24 closed boundary."""

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


def test_y25_prereg_locked_and_y24_closed() -> None:
    raw = json.loads((ART / "Y25-PREREG.json").read_text(encoding="utf-8"))
    closed = json.loads((Y24 / "Y24_CLOSED.json").read_text(encoding="utf-8"))
    assert raw["status"] == "PREREG_LOCKED"
    assert raw["protocol_id"] == "Y25-MV-v1"
    assert raw["arms_started"] is False
    assert raw["hypotheses"]["requires_unseen_variant"] is True
    assert raw["mcid"]["MEMORY_COST_RATIO_MAX"] == 0.6
    assert closed["status"] == "CAMPAIGN_CLOSED"
    assert closed["adaptive_c_advantage"] == "NOT_SHOWN_REJECTED_UNDER_PROTOCOL"
    assert closed["post_hoc_y24_rescue_forbidden"] is True
    assert "CAMPAIGN_CLOSED" in (Y24 / "Y24_CLOSED.md").read_text(encoding="utf-8")


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


def test_y25_stub_refuses_before_unseal() -> None:
    with pytest.raises(RuntimeError, match="holdout not UNSEALED"):
        run_arm_stub("W1", {"task_id": "x"})


def test_y25_does_not_claim_y24_memory_support() -> None:
    claims = (ART / "CLAIMS.md").read_text(encoding="utf-8")
    assert "Y24 H_memory INCONCLUSIVE as SUPPORT" in claims
    prereg = (ART / "Y25-PREREG.md").read_text(encoding="utf-8")
    assert "INCONCLUSIVE" in prereg
    assert "Trust Kernel" in prereg
