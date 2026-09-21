from __future__ import annotations

from global_os.verification import (
    ResultClass,
    VerificationRequest,
    VerificationRouter,
    VerificationTier,
)
from global_os.verification.independent_stack import (
    IndependentVerificationStack,
    MethodResult,
    MethodSpec,
    numeric_independent_stack,
)


def test_stack_rejects_same_model_family_only():
    stack = IndependentVerificationStack(
        (
            MethodSpec(
                method_id="judge_a",
                family="llm_judge",
                diversity_axis="different_provider",
                provider="openai",
                model_family="gpt",
                run=lambda _p: MethodResult("judge_a", True, {}),
            ),
            MethodSpec(
                method_id="judge_b",
                family="llm_judge",
                diversity_axis="different_model_family",
                provider="openai",
                model_family="gpt",
                run=lambda _p: MethodResult("judge_b", True, {}),
            ),
        )
    )
    out = stack.verify({}, required_tier=VerificationTier.INDEPENDENT.value)
    assert out.passed is False
    assert out.consensus == "insufficient_diversity"
    assert "GOS-I10" in out.details["reason"]


def test_stack_requires_two_distinct_axes_for_independent_tier():
    stack = IndependentVerificationStack(
        (
            MethodSpec(
                method_id="only",
                family="deterministic",
                diversity_axis="deterministic_recompute",
                run=lambda _p: MethodResult("only", True, {}),
            ),
        )
    )
    out = stack.verify({}, required_tier=VerificationTier.INDEPENDENT.value)
    assert out.passed is False
    assert out.consensus == "insufficient_diversity"


def test_numeric_dual_stack_unanimous_pass_and_conflict():
    stack = numeric_independent_stack()
    ok = stack.verify(
        {"expected": 42, "actual": 42},
        required_tier=VerificationTier.INDEPENDENT.value,
    )
    assert ok.passed is True
    assert ok.consensus == "unanimous_pass"
    assert "deterministic_recompute" in ok.diversity_factors
    assert "different_algorithm" in ok.diversity_factors

    conflict = stack.verify(
        {"expected": 42, "actual": 41},
        required_tier=VerificationTier.INDEPENDENT.value,
    )
    assert conflict.passed is False
    assert conflict.consensus in {"unanimous_fail", "conflicted"}


def test_router_uses_independent_stack_for_high_impact_numeric():
    router = VerificationRouter()
    out = router.route(
        VerificationRequest(
            result_class=ResultClass.NUMERIC,
            payload={"expected": 7, "actual": 7},
            impact="high",
            irreversibility="moderate",
        )
    )
    assert out.passed is True
    assert out.protocol == "independent_multi_method"
    assert len(out.diversity_factors) >= 2
    assert "same_model" not in "".join(out.diversity_factors)
