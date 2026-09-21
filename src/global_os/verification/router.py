"""Verification Router — classifies results and selects protocol (not LLM critic)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from global_os.verification.diversity import meets_tier_diversity
from global_os.verification.independent_stack import (
    IndependentVerificationStack,
    numeric_independent_stack,
)


class ResultClass(str, Enum):
    NUMERIC = "numeric"
    CODE = "code"
    FACTUAL = "factual"
    SOURCE_DERIVED = "source_derived"
    FORECAST = "forecast"
    CAUSAL = "causal"
    POLICY = "policy"
    HIGH_IMPACT_ACTION = "high_impact_action"


class VerificationTier(int, Enum):
    NONE = 0
    DETERMINISTIC = 1
    INDEPENDENT = 2
    DIVERSE_EXTERNAL = 3
    HUMAN = 4


@dataclass(frozen=True)
class VerificationRequest:
    result_class: ResultClass
    payload: dict[str, Any]
    impact: str = "low"
    irreversibility: str = "none"
    uncertainty: str = "medium"


@dataclass(frozen=True)
class VerificationOutcome:
    protocol: str
    tier: VerificationTier
    passed: bool
    details: dict[str, Any]
    diversity_factors: tuple[str, ...]


Verifier = Callable[[dict[str, Any]], VerificationOutcome]


def required_tier(req: VerificationRequest) -> VerificationTier:
    score = 0
    if req.impact in {"high", "critical"}:
        score += 2
    if req.irreversibility in {"moderate", "high"}:
        score += 2
    if req.uncertainty in {"high", "very_high"}:
        score += 1
    if req.result_class == ResultClass.HIGH_IMPACT_ACTION:
        score += 2
    if score >= 5:
        return VerificationTier.HUMAN
    if score >= 3:
        return VerificationTier.DIVERSE_EXTERNAL
    if score >= 2:
        return VerificationTier.INDEPENDENT
    if score >= 1:
        return VerificationTier.DETERMINISTIC
    return VerificationTier.NONE


def deterministic_numeric_verifier(payload: dict[str, Any]) -> VerificationOutcome:
    expected = payload.get("expected")
    actual = payload.get("actual")
    passed = expected == actual
    return VerificationOutcome(
        protocol="independent_recomputation",
        tier=VerificationTier.DETERMINISTIC,
        passed=passed,
        details={"expected": expected, "actual": actual},
        diversity_factors=("different_algorithm", "deterministic_recompute"),
    )


class VerificationRouter:
    def __init__(self) -> None:
        self._verifiers: dict[ResultClass, Verifier] = {
            ResultClass.NUMERIC: deterministic_numeric_verifier,
        }
        self._stacks: dict[ResultClass, IndependentVerificationStack] = {
            ResultClass.NUMERIC: numeric_independent_stack(),
        }

    def register(self, result_class: ResultClass, verifier: Verifier) -> None:
        self._verifiers[result_class] = verifier

    def register_stack(
        self, result_class: ResultClass, stack: IndependentVerificationStack
    ) -> None:
        self._stacks[result_class] = stack

    def route(self, request: VerificationRequest) -> VerificationOutcome:
        tier = required_tier(request)
        stack = self._stacks.get(request.result_class)
        if stack is not None and tier.value >= VerificationTier.INDEPENDENT.value:
            stack_out = stack.verify(request.payload, required_tier=tier.value)
            return stack_out.as_verification_outcome(tier=tier)

        verifier = self._verifiers.get(request.result_class)
        if verifier is None:
            return VerificationOutcome(
                protocol="unsupported",
                tier=tier,
                passed=False,
                details={"reason": f"no verifier for {request.result_class}"},
                diversity_factors=(),
            )
        outcome = verifier(request.payload)
        if not meets_tier_diversity(tier.value, outcome.diversity_factors):
            return VerificationOutcome(
                protocol=outcome.protocol,
                tier=tier,
                passed=False,
                details={
                    "reason": "insufficient verification diversity (GOS-I10)",
                    "claimed_factors": list(outcome.diversity_factors),
                },
                diversity_factors=outcome.diversity_factors,
            )
        return VerificationOutcome(
            protocol=outcome.protocol,
            tier=tier,
            passed=outcome.passed,
            details=outcome.details,
            diversity_factors=outcome.diversity_factors,
        )
