"""Acceptance tests — Empirical Science freeze artifacts."""

from __future__ import annotations

from global_os.evals.environment.hrsn_experiment import run_hrsn_policies
from global_os.evals.environment.ladder import LADDER, SCORE_FIELDS, run_henv_ladder
from global_os.evals.integrity import (
    HARD_GATES,
    GateResult,
    SoftMetrics,
    all_pass_gates,
    score_goal_integrity,
)
from global_os.evals.maturity import audit_capability_matrix
from global_os.evals.organization.hypotheses import HYPOTHESES, summarize_horg_family
from global_os.evals.survival.wall_clock_schedule import (
    WALL_CLOCK_48H_SCHEDULE,
    schedule_as_dict,
    validate_schedule,
)
from tests.support.scripted_hetero_provider import ScriptedHeterogeneousProvider


def test_goal_integrity_any_hard_fail_is_fail():
    gates = {g: "PASS" for g in HARD_GATES}
    gates["authority_boundary_preserved"] = "FAIL"
    score = score_goal_integrity(gates, soft=SoftMetrics(completion=0.99, quality=0.99))
    assert score.survival == GateResult.FAIL
    assert score.as_dict()["soft"]["completion"] == 0.99  # soft never rescues


def test_goal_integrity_incomplete_gates_fail_closed():
    score = score_goal_integrity({"goal_semantics_preserved": "PASS"})
    assert score.survival == GateResult.FAIL
    assert score.gates["recovery_successful"] == GateResult.FAIL


def test_goal_integrity_all_pass():
    score = score_goal_integrity(all_pass_gates())
    assert score.survival == GateResult.PASS
    assert len(score.gates) == 8


def test_henv_ladder_does_not_require_e_to_win():
    # Scripted hetero answers arithmetic in prompt; customize provider briefly
    class _Arith(ScriptedHeterogeneousProvider):
        def generate(self, request):  # type: ignore[no-untyped-def]
            from global_os.adapters.models.base import GenerateResponse, ModelRef

            return GenerateResponse(
                text="399",
                model=ModelRef("scripted", "arith", "0"),
                input_tokens=1,
                output_tokens=1,
                latency_ms=1.0,
                cost_usd=0.0,
            )

    report = run_henv_ladder(_Arith(), fidelity="PROVIDER_WIRE")
    d = report.as_dict()
    assert d["e_required_to_win"] is False
    assert d["scientific_claim_accepted"] is False
    assert len(d["trials"]) == 5
    assert {t["level"] for t in d["trials"]} == {lv for lv, _ in LADDER}
    assert set(SCORE_FIELDS).issubset(d["trials"][0]["scores"])
    assert d["winner"] is not None


def test_hrsn_vuw_per_cost_and_gos_i23():
    report = run_hrsn_policies()
    d = report.as_dict()
    assert d["gos_i23_ok"] is True
    assert d["scientific_claim_accepted"] is False
    assert d["primary_metric"] == "VerifiedUsefulWork/Cost"
    policies = {t["policy"] for t in d["trials"]}
    assert policies == {"fixed_low", "fixed_medium", "fixed_high", "adaptive"}
    assert all(t["verification_tier"] == 2 for t in d["trials"])


def test_horg_family_split_four_hypotheses_no_acceptance():
    report = summarize_horg_family()
    d = report.as_dict()
    assert set(d["hypotheses"]) == set(HYPOTHESES)
    assert all(v is False for v in d["scientific_claims_accepted"].values())
    assert set(d["conditional_winners"]) == {
        "highly_parallel",
        "mixed_dependencies",
        "strongly_sequential",
    }
    # Conditional pattern: sequential → single often best; parallel → manager/adaptive
    assert d["conditional_winners"]["strongly_sequential"] in {
        "strong_single",
        "adaptive",
    }
    assert d["verdict"] == "SYNTHETIC_CONDITIONAL_MAP_NOT_PROOF"


def test_wall_clock_48h_schedule_contract():
    validate_schedule()
    d = schedule_as_dict()
    assert d["duration_hours"] == 48.0
    assert d["ci_policy"] == "not_on_every_pr"
    assert d["gates"]["weekly_or_rc"] == "wall_clock_48h"
    assert len(WALL_CLOCK_48H_SCHEDULE) == 9
    assert WALL_CLOCK_48H_SCHEDULE[0].offset_hours == 2.0
    assert WALL_CLOCK_48H_SCHEDULE[-1].offset_hours == 42.0


def test_capability_self_audit_runs_on_matrix():
    report = audit_capability_matrix()
    assert report["capability_count"] >= 50
    assert "overstated_count" in report
    assert isinstance(report["rows"], list)
    assert report["rows"][0]["maturity"]
