from __future__ import annotations

from global_os.evals.evaluators import summarize_h_ctx_001, summarize_h_eval_001
from global_os.verification import (
    ResultClass,
    VerificationOutcome,
    VerificationRequest,
    VerificationRouter,
    VerificationTier,
    assess_diversity,
)


def test_h_eval_001_inconclusive_and_no_kappa():
    report = summarize_h_eval_001()
    assert report["verdict"] == "INCONCLUSIVE_NEEDS_REAL_MODEL"
    assert report["kappa_threshold"] is None
    assert report["escaped_errors"]["calibrated_stack"] < report["escaped_errors"]["raw_judge"]


def test_h_ctx_001_structured_retains_more_critical():
    report = summarize_h_ctx_001()
    assert report["verdict"] == "INCONCLUSIVE_NEEDS_REAL_MODEL"
    assert (
        report["metrics"]["structured_critical_retention"]
        > report["metrics"]["compaction_round3_critical_retention"]
    )


def test_diversity_rejects_same_model_only():
    bad = assess_diversity(("same_model_instance_2",))
    assert bad.independent is False
    good = assess_diversity(("different_provider", "different_source"))
    assert good.independent is True


def test_router_rejects_insufficient_diversity_on_independent_tier():
    router = VerificationRouter()

    def same_model_verifier(_payload: dict) -> VerificationOutcome:
        return VerificationOutcome(
            protocol="llm_judge",
            tier=VerificationTier.INDEPENDENT,
            passed=True,
            details={},
            diversity_factors=("same_model_instance_2",),
        )

    router.register(ResultClass.FACTUAL, same_model_verifier)
    out = router.route(
        VerificationRequest(
            result_class=ResultClass.FACTUAL,
            payload={},
            impact="high",
            irreversibility="moderate",
        )
    )
    assert out.passed is False
    assert "GOS-I10" in out.details["reason"]
