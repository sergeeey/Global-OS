"""Acceptance: Y24 prereg + rubric/cost/isolation locks; no premature execution."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from global_os.evals.research.y24_arms import run_arm_stub
from global_os.evals.research.y24_complexity import assign_stratum, stratum_from_features
from global_os.evals.research.y24_cost import cost_match_ok, verification_cost
from global_os.evals.research.y24_gates import memory_pair_valid, refuse_arm_execution

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
    assert st["phase"].startswith("PREREG_LOCKED")
    assert st["arms_started"] is False
    assert st["t3_not_evidence"] is True
    assert st["trust_kernel_promoted"] is False
    assert st["c2_edited"] is False


def test_y24_rubric_cost_isolation_locked() -> None:
    raw = json.loads((ART / "Y24-PREREG.json").read_text(encoding="utf-8"))
    assert raw["complexity_rubric"]["status"] == "RUBRIC_LOCKED"
    assert raw["complexity_rubric"]["post_hoc_relabel_forbidden"] is True
    assert raw["cost_accounting"]["status"] == "COST_ACCOUNTING_LOCKED"
    assert raw["isolation"]["status"] == "ISOLATION_GATE_LOCKED"
    assert raw["isolation"][
        "arm_c_memory_builders_forbidden_sealed_access_before_unseal"
    ] is True
    assert (ART / "Y24-COMPLEXITY-RUBRIC.json").is_file()
    assert (ART / "Y24-COST-ACCOUNTING.md").is_file()
    assert (ART / "Y24-ISOLATION.md").is_file()
    assert (ART / "Y24-SEAL-CHECKLIST.md").is_file()
    assert "post_hoc_stratum_relabel" in raw["forbidden"]
    assert "arm_c_builder_access_sealed_holdout_before_unseal" in raw["forbidden"]
    assert "h_memory_same_case_not_unseen_variant" in raw["forbidden"]
    weights = raw["verification_cost_formula"]["weights"]
    assert "verification_calls" in weights
    assert "recovery_overhead_seconds" in weights


def test_y24_arms_metrics_and_decision_surface() -> None:
    raw = json.loads((ART / "Y24-PREREG.json").read_text(encoding="utf-8"))
    assert set(raw["arms"]) == {"A", "B", "C"}
    assert "benign_suspicious" in raw["task_labels"]
    assert raw["benign_suspicious_min_fraction_of_benign"] >= 0.3
    assert set(raw["complexity_strata"]) == {"LOW", "MEDIUM", "HIGH"}
    assert raw["decision"]["require_cost_match_in_winning_stratum"] is True
    assert raw["hypotheses"]["H_memory_requires_unseen_variant"] is True
    assert raw["y23_forbidden"] is True
    assert raw["legacy_y19_status"] == "FROZEN_DO_NOT_REOPEN"


def test_y24_complexity_stratum_boundaries() -> None:
    assert assign_stratum(0) == "LOW"
    assert assign_stratum(3) == "LOW"
    assert assign_stratum(4) == "MEDIUM"
    assert assign_stratum(6) == "MEDIUM"
    assert assign_stratum(7) == "HIGH"
    assert assign_stratum(10) == "HIGH"
    score, stratum = stratum_from_features(
        {
            "F_decomp": 2,
            "F_deps": 2,
            "F_vdepth": 2,
            "F_horizon": 1,
            "F_ext": 0,
        }
    )
    assert score == 7
    assert stratum == "HIGH"


def test_y24_cost_match_and_ledger() -> None:
    ledger = {
        "llm_cost_tokens": 1000,
        "tool_calls": 2,
        "human_interventions": 0,
        "latency_ms": 1000,
        "verification_calls": 1,
        "recovery_overhead_seconds": 0,
    }
    cost = verification_cost(ledger)
    assert cost == pytest.approx(1000 + 100 + 1 + 100)
    assert cost_match_ok(100.0, 125.0) is True
    assert cost_match_ok(100.0, 125.1) is False


def test_y24_memory_pair_requires_unseen_variant() -> None:
    first = {
        "task_id": "t1",
        "failure_class": "auth_expand",
        "patch_ref": "p1",
        "memory_pair_id": "m1",
        "memory_role": "first",
    }
    same = dict(first)
    same["memory_role"] = "unseen_variant"
    assert memory_pair_valid(first, same) is False  # same task_id/patch
    variant = {
        "task_id": "t2",
        "failure_class": "auth_expand",
        "patch_ref": "p2",
        "memory_pair_id": "m1",
        "memory_role": "unseen_variant",
    }
    assert memory_pair_valid(first, variant) is True


def test_y24_refuse_arm_execution_until_unseal() -> None:
    with pytest.raises(RuntimeError, match="holdout not UNSEALED"):
        refuse_arm_execution(ROOT)
    with pytest.raises(RuntimeError, match="holdout not UNSEALED"):
        run_arm_stub("C", {"task_id": "x"})


def test_y24_holdout_not_sealed_yet() -> None:
    man = json.loads((ART / "sealed" / "HOLDOUT_MANIFEST.json").read_text(encoding="utf-8"))
    assert man["status"] == "NOT_SEALED_YET"
    assert man["unsealed_for_execution"] is False
    assert man["tasks"] == []
    assert not (ART / "sealed" / "holdout_labels.json").exists()


def test_y24_naming_collision_documented() -> None:
    raw = json.loads((ART / "Y24-PREREG.json").read_text(encoding="utf-8"))
    assert raw["campaign_id"] == "Y24"
    assert raw["informal_brief_name"] == "Y19_adaptive_verifier_threshold"
    legacy = ROOT / "artifacts" / "y19" / "CLAIMS.md"
    assert legacy.is_file()
    assert "FROZEN" in legacy.read_text(encoding="utf-8")
