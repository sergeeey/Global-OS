from __future__ import annotations

from global_os.verification import (
    ResultClass,
    VerificationRequest,
    VerificationRouter,
    VerificationOutcome,
    VerificationTier,
    required_tier,
)


def test_verification_router_numeric_and_tier():
    router = VerificationRouter()
    req = VerificationRequest(
        result_class=ResultClass.NUMERIC,
        payload={"expected": 4, "actual": 4},
        impact="low",
    )
    out = router.route(req)
    assert out.passed is True
    assert out.protocol == "independent_recomputation"
    assert "same_model_instance_2" not in out.diversity_factors

    high = VerificationRequest(
        result_class=ResultClass.HIGH_IMPACT_ACTION,
        payload={},
        impact="critical",
        irreversibility="high",
    )
    assert required_tier(high) >= VerificationTier.DIVERSE_EXTERNAL


def test_human_tier_does_not_pass_by_label_alone():
    """Regression: HUMAN must require human_reference — not dual-deterministic pass."""
    router = VerificationRouter()
    req = VerificationRequest(
        result_class=ResultClass.NUMERIC,
        payload={"expected": 1, "actual": 1},
        impact="critical",
        irreversibility="high",
        uncertainty="high",
    )
    assert required_tier(req) == VerificationTier.HUMAN
    out = router.route(req)
    assert out.tier == VerificationTier.HUMAN
    assert out.passed is False
    assert "human_reference" in out.details.get("reason", "")


def test_human_tier_passes_when_human_reference_present():
    router = VerificationRouter()

    def human_ok(payload: dict) -> VerificationOutcome:
        del payload
        return VerificationOutcome(
            protocol="human_review",
            tier=VerificationTier.HUMAN,
            passed=True,
            details={"reviewer": "operator"},
            diversity_factors=("human_reference", "different_source"),
        )

    router.register(ResultClass.FACTUAL, human_ok)
    # Force FACTUAL path without numeric stack: use FACTUAL + HUMAN score
    req = VerificationRequest(
        result_class=ResultClass.FACTUAL,
        payload={"claim": "x"},
        impact="critical",
        irreversibility="high",
        uncertainty="high",
    )
    assert required_tier(req) == VerificationTier.HUMAN
    out = router.route(req)
    assert out.passed is True
    assert "human_reference" in out.diversity_factors
