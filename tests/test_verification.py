from __future__ import annotations

from global_os.verification import (
    ResultClass,
    VerificationRequest,
    VerificationRouter,
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
