"""Acceptance: frozen C2 contract + T3 prereg discipline."""

from __future__ import annotations

import json
from pathlib import Path

from global_os.evals.trust.recovery_router import HARD_BLOCK_FAULTS, RECOVERABLE_FAULTS

ROOT = Path(__file__).resolve().parents[1]
T1 = ROOT / "artifacts" / "safe_autonomy_t1"


def test_selective_bounded_recovery_contract_matches_code() -> None:
    raw = json.loads((T1 / "SELECTIVE_BOUNDED_RECOVERY_V1.json").read_text(encoding="utf-8"))
    assert raw["status"] == "MECHANISM_FROZEN_CANDIDATE"
    assert raw["trust_zone"] == "T2_EVAL_HARNESS"
    assert set(raw["hard_block_fault_classes"]) == set(HARD_BLOCK_FAULTS)
    assert set(raw["recoverable_fault_classes"]) == set(RECOVERABLE_FAULTS)
    assert raw["reverify_requires"]["llm_sole_oracle_forbidden"] is True
    assert raw["pinned_experiment_sha"] == (
        T1 / "T2_EXPERIMENT_SHA.txt"
    ).read_text(encoding="utf-8").strip()
    assert (T1 / "SELECTIVE_BOUNDED_RECOVERY_V1.md").is_file()


def test_t2_independent_review_present() -> None:
    md = T1 / "T2" / "T2_INDEPENDENT_REVIEW.md"
    js = T1 / "T2" / "T2_INDEPENDENT_REVIEW.json"
    assert md.is_file() and js.is_file()
    raw = json.loads(js.read_text(encoding="utf-8"))
    assert raw["t2_verdict_confirmed"] == "KEEP"
    assert raw["integrity_pass"] is True
    assert raw["trust_kernel_promote"] is False
    assert "CONFIRM KEEP" in md.read_text(encoding="utf-8")


def test_t3_prereg_locked_mechanism_pin() -> None:
    md = T1 / "T3_PREREG.md"
    js = T1 / "T3_PREREG.json"
    assert md.is_file() and js.is_file()
    raw = json.loads(js.read_text(encoding="utf-8"))
    assert raw["status"] == "PREREG_LOCKED"
    assert raw["protocol_id"] == "SAFE_AUTONOMY_T3-v1"
    assert raw["frozen_mechanism"] == "SELECTIVE_BOUNDED_RECOVERY-v1"
    pin = (T1 / "T2_EXPERIMENT_SHA.txt").read_text(encoding="utf-8").strip()
    assert raw["mechanism_pin_sha"] == pin
    assert "edit_c2_after_holdout_unseal" in raw["forbidden"]
    assert "pass_at_1_as_primary" in raw["forbidden"]
    assert raw["urr_hard_gate"] == 0.0
    assert raw["min_runs_per_arm_seed_condition"] >= 3
    text = md.read_text(encoding="utf-8")
    assert "INCONCLUSIVE" in text
    assert "Trust Kernel" in text or "trust kernel" in text.lower()


def test_allowed_claim_language_present() -> None:
    contract = (T1 / "SELECTIVE_BOUNDED_RECOVERY_V1.md").read_text(encoding="utf-8")
    assert "KEEP for further" in contract or "KEEP for further generalization" in contract
    assert "H_TRUST proven in general" in contract or "h_trust_proven_in_general" in (
        T1 / "SELECTIVE_BOUNDED_RECOVERY_V1.json"
    ).read_text(encoding="utf-8")
