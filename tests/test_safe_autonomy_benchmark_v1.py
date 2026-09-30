"""Acceptance tests for SAFE_AUTONOMY_BENCHMARK-v1 metrics freeze."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from global_os.evals.trust.safe_autonomy_metrics import (
    FAULT_INJECTION_CLASSES,
    MATERIAL_FAILURE_TAXONOMY,
    MCID_SET,
    MCID_UNSET,
    ArmMetrics,
    compute_mier,
    compute_ssr,
    decide_keep_reject,
    load_benchmark_freeze,
)

ROOT = Path(__file__).resolve().parents[1]
FREEZE_JSON = ROOT / "artifacts/hardening/SAFE_AUTONOMY_BENCHMARK_V1.json"
FREEZE_MD = ROOT / "artifacts/hardening/SAFE_AUTONOMY_BENCHMARK_V1.md"


def test_freeze_files_exist() -> None:
    assert FREEZE_JSON.is_file()
    assert FREEZE_MD.is_file()


def test_load_benchmark_freeze_locked() -> None:
    raw = load_benchmark_freeze()
    assert raw["status"] == "METRICS_FROZEN"
    assert raw["arms_started"] in (False, True)
    assert raw["mcid"]["status"] in (MCID_UNSET, MCID_SET)
    if raw["mcid"]["status"] == MCID_SET:
        assert float(raw["mcid"]["mier_win_abs"]) > 0
        assert float(raw["mcid"]["ssr_win_abs"]) > 0
    assert tuple(raw["material_failure_taxonomy"]) == MATERIAL_FAILURE_TAXONOMY
    assert tuple(raw["fault_injection_classes"]) == FAULT_INJECTION_CLASSES
    assert set(raw["arms"]) == {"A", "B", "C"}
    assert "fixed_resource" in raw["modes"]
    assert "cost_normalized_frontier" in raw["modes"]


def test_freeze_json_bound_to_m15_provenance() -> None:
    raw = json.loads(FREEZE_JSON.read_text(encoding="utf-8"))
    assert raw["post_m15"]["exam_sha"].startswith("7ab345e")
    assert raw["post_m15"]["audit_sha"].startswith("a7960d9")
    assert raw["post_m15"]["decision"] == "M1.5_CLOSED_SCOPE_LIMITED"


def test_compute_mier_and_ssr() -> None:
    assert compute_mier(n_material_escapes=2, n_consequential_actions=10) == 0.2
    assert compute_ssr(n_missions_useful_and_zero_escapes=7, n_missions=10) == 0.7


def test_mier_fail_closed_zero_denominator() -> None:
    with pytest.raises(ValueError):
        compute_mier(n_material_escapes=0, n_consequential_actions=0)


def test_ssr_fail_closed_overcount() -> None:
    with pytest.raises(ValueError):
        compute_ssr(n_missions_useful_and_zero_escapes=3, n_missions=2)


def _arm(
    arm_id: str,
    *,
    escapes: int,
    actions: int = 100,
    useful_safe: int = 80,
    missions: int = 100,
    attention: float = 10.0,
    tokens: float = 1000.0,
    completion: float = 0.9,
    mode_b: bool = True,
) -> ArmMetrics:
    return ArmMetrics(
        arm_id=arm_id,
        n_material_escapes=escapes,
        n_consequential_actions=actions,
        n_missions_useful_and_zero_escapes=useful_safe,
        n_missions=missions,
        human_attention_minutes=attention,
        cost_tokens=tokens,
        completion_rate=completion,
        mode_b_frontier_reported=mode_b,
    )


def test_keep_when_c_clearly_better() -> None:
    d = decide_keep_reject(
        arm_a=_arm("A", escapes=20, useful_safe=60),
        arm_b=_arm("B", escapes=15, useful_safe=65),
        arm_c=_arm("C", escapes=5, useful_safe=70),
    )
    assert d.verdict == "KEEP"
    assert d.mier["C"] < d.mier["A"]
    assert d.mier["C"] < d.mier["B"]


def test_reject_when_c_approx_b() -> None:
    d = decide_keep_reject(
        arm_a=_arm("A", escapes=20),
        arm_b=_arm("B", escapes=10),
        arm_c=_arm("C", escapes=10),
    )
    assert d.verdict == "REJECT"
    assert "C_approx_B_on_mier" in d.reasons


def test_reject_verifier_tax() -> None:
    d = decide_keep_reject(
        arm_a=_arm("A", escapes=20, useful_safe=80, completion=0.9),
        arm_b=_arm("B", escapes=15, useful_safe=70, completion=0.85),
        arm_c=_arm("C", escapes=2, useful_safe=20, completion=0.3),
    )
    assert d.verdict == "REJECT"
    assert any(r.startswith("verifier_tax") for r in d.reasons)


def test_reject_llm_sole_oracle() -> None:
    d = decide_keep_reject(
        arm_a=_arm("A", escapes=20),
        arm_b=_arm("B", escapes=15),
        arm_c=_arm("C", escapes=1),
        llm_sole_oracle=True,
    )
    assert d.verdict == "REJECT"
    assert d.reasons == ["llm_sole_mode_oracle"]


def test_invalid_without_mode_b() -> None:
    d = decide_keep_reject(
        arm_a=_arm("A", escapes=20, mode_b=False),
        arm_b=_arm("B", escapes=15, mode_b=True),
        arm_c=_arm("C", escapes=1, mode_b=True),
    )
    assert d.verdict == "INVALID"
    assert "mode_B_frontier_not_reported" in d.reasons


def test_md_mentions_mcid_amendment() -> None:
    text = FREEZE_MD.read_text(encoding="utf-8")
    assert "SET_BY_VARIANCE_PILOT_v1" in text
    assert "METRICS_FROZEN" in text
    assert "KEEP" in text and "REJECT" in text
    assert "mier_win_abs" in text
