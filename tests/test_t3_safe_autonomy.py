"""Acceptance tests for T3 harness, PACK-v3 seal, audit checklist, decision gates."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from global_os.evals.trust.pack_v3 import (
    PACK_V3_ID,
    assert_pack_v3_integrity,
    build_pack_v3_sealed,
    freeze_pack_v3,
    unseal_pack_v3,
)
from global_os.evals.trust.safe_autonomy_metrics import ArmMetrics
from global_os.evals.trust.t2_metrics import T2DiagnosticMetrics
from global_os.evals.trust.t3_arm_runners import run_t3_arm_once, run_t3_layer
from global_os.evals.trust.t3_metrics import (
    decide_t3,
    extract_t3_diagnostics,
    merge_seed_trajectories,
)
from global_os.evals.trust.t3_protocol import (
    CONTINUATION_BINDING_TEXT,
    FAILURE_ATTRIBUTION_CLASSES,
    MECHANISM_PIN_SHA,
    PACK_V3_UNSEALED_AT_SHA,
    T3_PROTOCOL_ID,
    assert_audit_checklist,
    assert_continuation_integrity,
    assert_mechanism_pin,
    assert_prereg_locked,
)
from global_os.evals.trust.t3_runner import freeze_t3_experiment_sha, run_t3

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "safe_autonomy_t1"


def test_audit_checklist_locked() -> None:
    assert_audit_checklist(ROOT)
    raw = json.loads((ART / "T3_AUDIT_CHECKLIST.json").read_text(encoding="utf-8"))
    assert set(raw["required_sections"]) == {
        "model_provider_provenance",
        "run_level_independence",
        "cost_recovery_tax",
        "failure_attribution",
    }
    assert set(raw["failure_attribution_classes"]) == set(FAILURE_ATTRIBUTION_CLASSES)


def test_mechanism_pin_and_prereg() -> None:
    assert_prereg_locked(ROOT)
    c = assert_mechanism_pin(ROOT)
    assert c["pinned_experiment_sha"] == MECHANISM_PIN_SHA


def test_pack_v3_seal_in_tmp(tmp_path: Path) -> None:
    man = freeze_pack_v3(root=tmp_path)
    assert man["pack_id"] == PACK_V3_ID
    assert man["status"] == "FROZEN_UNSEEN"
    assert (tmp_path / "PACK_V3" / "sealed" / "sealed_pack.json").is_file()
    assert_pack_v3_integrity(root=tmp_path)
    with pytest.raises(ValueError, match="experiment_sha"):
        unseal_pack_v3(root=tmp_path, experiment_sha="", protocol_id=T3_PROTOCOL_ID)
    pack = unseal_pack_v3(
        root=tmp_path, experiment_sha="abc123", protocol_id=T3_PROTOCOL_ID
    )
    assert pack["status"] == "UNSEALED"
    assert pack["n_l1_missions"] > 0 and pack["n_l2_missions"] >= 2


def test_run_independence_and_attribution() -> None:
    pack = build_pack_v3_sealed()
    r1 = run_t3_arm_once(
        arm_id="C2",
        missions=pack["l1_missions"][:3],
        seed=301,
        prefer_live=False,
    )
    r2 = run_t3_arm_once(
        arm_id="C2",
        missions=pack["l1_missions"][:3],
        seed=302,
        prefer_live=False,
    )
    assert r1["run_independence"] is True
    assert r2["run_independence"] is True
    assert "cost_recovery_tax" in r1
    assert set(r1["failure_attribution_counts"]).issubset(FAILURE_ATTRIBUTION_CLASSES)
    assert r1["provenance_samples"]
    assert r1["provenance_samples"][0]["fidelity"] in {
        "SCRIPTED_PROXY",
        "LIVE_BLOCKED",
        "LIVE_LLM",
    }


def test_l2_natural_hooks_produce_recoverable() -> None:
    pack = build_pack_v3_sealed()
    layer = run_t3_layer(pack=pack, layer="L2", seeds=(301,), prefer_live=False)
    merged = merge_seed_trajectories(layer["arms"]["C2"])
    diag = extract_t3_diagnostics(merged)
    assert diag.n_recoverable_fault_missions > 0
    assert diag.urr == 0.0


def test_decide_t3_inconclusive_without_live() -> None:
    def _arm(aid: str) -> ArmMetrics:
        return ArmMetrics(
            arm_id=aid,
            n_material_escapes=0 if aid == "C2" else 50,
            n_consequential_actions=100,
            n_missions_useful_and_zero_escapes=70 if aid == "C2" else 10,
            n_missions=100,
            human_attention_minutes=0.0,
            cost_tokens=100.0,
            completion_rate=0.7 if aid == "C2" else 1.0,
            mode_b_frontier_reported=True,
        )

    diag = T2DiagnosticMetrics(
        fsr=0.5,
        hbr=0.2,
        urr=0.0,
        n_recoverable_fault_missions=20,
        n_useful_recovered=10,
        n_fault_missions=30,
        n_hard_blocked_no_useful=6,
        n_recovery_attempts=10,
        n_unsafe_recovery_escapes=0,
    )
    d = decide_t3(
        arm_a=_arm("A"),
        arm_b=_arm("B"),
        arm_c2=_arm("C2"),
        diagnostics_c2=diag,
        n_seeds=3,
        live_ready=False,
        fidelity="LIVE_BLOCKED",
        mechanism_pin_ok=True,
        mode_b_frontier_reported=True,
        audit_fields_complete=True,
        l2_recoverable_n=4,
    )
    assert d.verdict == "INCONCLUSIVE"
    assert "provider_key_unavailable_live_layer" in d.reasons


def test_decide_t3_inconclusive_quota_exhausted() -> None:
    def _arm(aid: str) -> ArmMetrics:
        return ArmMetrics(
            arm_id=aid,
            n_material_escapes=0 if aid == "C2" else 50,
            n_consequential_actions=100,
            n_missions_useful_and_zero_escapes=70 if aid == "C2" else 10,
            n_missions=100,
            human_attention_minutes=0.0,
            cost_tokens=100.0,
            completion_rate=0.7 if aid == "C2" else 1.0,
            mode_b_frontier_reported=True,
        )

    diag = T2DiagnosticMetrics(
        fsr=0.5,
        hbr=0.2,
        urr=0.0,
        n_recoverable_fault_missions=20,
        n_useful_recovered=10,
        n_fault_missions=30,
        n_hard_blocked_no_useful=6,
        n_recovery_attempts=10,
        n_unsafe_recovery_escapes=0,
    )
    d = decide_t3(
        arm_a=_arm("A"),
        arm_b=_arm("B"),
        arm_c2=_arm("C2"),
        diagnostics_c2=diag,
        n_seeds=3,
        live_ready=True,
        fidelity="LIVE_BLOCKED",
        mechanism_pin_ok=True,
        mode_b_frontier_reported=True,
        audit_fields_complete=True,
        l2_recoverable_n=4,
        live_block_reason="provider_quota_exhausted_live_layer",
    )
    assert d.verdict == "INCONCLUSIVE"
    assert d.reasons == ["provider_quota_exhausted_live_layer"]


def test_run_t3_injected_pack_no_repo_unseal(tmp_path: Path) -> None:
    pack = build_pack_v3_sealed()
    sha_path = tmp_path / "T3_EXPERIMENT_SHA.txt"
    sha_path.write_text("testsha_t3\n", encoding="utf-8")

    import global_os.evals.trust.t3_protocol as tp
    import global_os.evals.trust.t3_runner as tr

    def _sha_path(root: Path | None = None) -> Path:
        del root
        return sha_path

    # Seal a temp pack_v3 so integrity check can pass when runner uses repo —
    # for injected path we skip unseal; still need pack_v3 integrity on repo.
    # Ensure repo pack exists or seal into repo if missing.
    from global_os.evals.trust.t3_runner import ensure_pack_v3_sealed

    ensure_pack_v3_sealed(root=ROOT)

    orig_tp = tp.t3_experiment_sha_path
    orig_tr = tr.t3_experiment_sha_path
    tp.t3_experiment_sha_path = _sha_path  # type: ignore[assignment]
    tr.t3_experiment_sha_path = _sha_path  # type: ignore[assignment]
    try:
        raw = run_t3(
            out_root=tmp_path / "t3_out",
            freeze_sha=False,
            unseal=False,
            pack=pack,
            prefer_live=False,
            seeds=(301, 302, 303),
        )
    finally:
        tp.t3_experiment_sha_path = orig_tp  # type: ignore[assignment]
        tr.t3_experiment_sha_path = orig_tr  # type: ignore[assignment]

    assert raw["protocol_id"] == T3_PROTOCOL_ID
    assert raw["decision"]["verdict"] in {"KEEP", "REJECT", "INCONCLUSIVE", "INVALID"}
    assert (tmp_path / "t3_out" / "T3_DECISION.md").is_file()
    assert raw["audit_checklist_complete"] is True
    # Without live keys, prefer_live=False → scripted smoke; verdict may be INCONCLUSIVE
    # only if prefer_live True. With prefer_live=False fidelity SCRIPTED_PROXY —
    # decide_t3 treats non-LIVE_BLOCKED + live_ready False as INCONCLUSIVE via live_ready.
    assert raw["live_ready"] is False or raw["fidelity"] != "LIVE_LLM"
    cont = raw["continuation"]
    assert cont["is_continuation_of_same_prereg"] is True
    assert cont["is_new_sealed_replication"] is False
    assert cont["create_pack_v4_now"] is False
    assert cont["pack_unsealed_at_experiment_sha"] == PACK_V3_UNSEALED_AT_SHA
    decision_md = (tmp_path / "t3_out" / "T3_DECISION.md").read_text(encoding="utf-8")
    assert "continuation of T3 under the same prereg" in decision_md
    assert "not a new sealed replication" in decision_md
    assert (tmp_path / "t3_out" / "LIVE_PROVENANCE.json").is_file()


def test_t3_continuation_attestation_present() -> None:
    md = ART / "T3" / "T3_CONTINUATION.md"
    js = ART / "T3" / "T3_CONTINUATION.json"
    assert md.is_file() and js.is_file()
    raw = json.loads(js.read_text(encoding="utf-8"))
    assert raw["status"] in {
        "AWAITING_LIVE_KEYS",
        "AWAITING_PROVIDER_QUOTA",
    }
    if raw["status"] == "AWAITING_PROVIDER_QUOTA":
        assert raw["block_reason"] == "provider_quota_exhausted_live_layer"
    assert raw["is_continuation_of_same_prereg"] is True
    assert raw["is_new_sealed_replication"] is False
    assert raw["create_pack_v4_now"] is False
    assert raw["post_unseal_changes"]["c2_recovery_router"] is False
    assert raw["pack_unsealed_at_experiment_sha"] == (
        ART / "T3_EXPERIMENT_SHA.txt"
    ).read_text(encoding="utf-8").strip()
    decision = (ART / "T3" / "T3_DECISION.md").read_text(encoding="utf-8")
    assert "continuation of T3 under the same prereg" in decision
    assert "not a new sealed replication" in decision
    assert CONTINUATION_BINDING_TEXT.splitlines()[0] in decision
    # Pin hashes must still match frozen files (fail-closed holdout integrity)
    att = assert_continuation_integrity(ROOT)
    assert att["pinned_hashes"]["t3_experiment_sha"] == PACK_V3_UNSEALED_AT_SHA


def test_decision_md_regen_preserves_continuation_binding() -> None:
    from global_os.evals.trust.t3_runner import _decision_md

    md = _decision_md(
        {
            "decision": {
                "verdict": "INCONCLUSIVE",
                "reasons": ["provider_key_unavailable_live_layer"],
                "stop_rule": "no_promote_rerun_or_park",
            },
            "generated_at_utc": "2026-09-30T00:00:00+00:00",
            "experiment_sha": PACK_V3_UNSEALED_AT_SHA,
            "protocol_id": T3_PROTOCOL_ID,
            "pack_id": "SAFE_AUTONOMY_PACK-v3",
            "execution_mode": "LIVE_BLOCKED_KEYS_UNAVAILABLE",
            "fidelity": "LIVE_BLOCKED",
            "live_ready": False,
            "mechanism_pin_sha": MECHANISM_PIN_SHA,
            "mechanism_contract": "SELECTIVE_BOUNDED_RECOVERY-v1",
            "layers": {
                "L1": {
                    "A": {"mier": 0.9, "ssr": 0.1, "flakiness": 0.0},
                    "B": {"mier": 0.8, "ssr": 0.1, "flakiness": 0.0},
                    "C2": {"mier": 0.0, "ssr": 0.8, "flakiness": 0.0},
                }
            },
            "diagnostics": {
                "L1_C2": {"fsr": 1.0, "urr": 0.0},
                "L2_C2": {"fsr": 1.0, "urr": 0.0},
            },
            "audit_checklist_complete": True,
            "seeds": [301, 302, 303],
            "harness_smoke_note": "test",
            "claim_scope": "test scope",
            "continuation": {
                "binding_text": CONTINUATION_BINDING_TEXT,
                "prior_run_archive": None,
            },
        }
    )
    assert "continuation of T3 under the same prereg" in md
    assert "not a new sealed replication" in md
    assert "PACK-v3 was unsealed at SHA c6523a6" in md


def test_freeze_t3_sha_write_once(tmp_path: Path) -> None:
    import global_os.evals.trust.t3_runner as tr

    path = tmp_path / "T3_EXPERIMENT_SHA.txt"

    def _sha_path(root: Path | None = None) -> Path:
        del root
        return path

    original = tr.t3_experiment_sha_path
    tr.t3_experiment_sha_path = _sha_path  # type: ignore[assignment]
    try:
        a = freeze_t3_experiment_sha(root=tmp_path, sha="deadbeef_t3")
        b = freeze_t3_experiment_sha(root=tmp_path, sha="deadbeef_t3")
        assert a == b == "deadbeef_t3"
        with pytest.raises(ValueError, match="already frozen"):
            freeze_t3_experiment_sha(root=tmp_path, sha="other")
    finally:
        tr.t3_experiment_sha_path = original  # type: ignore[assignment]
