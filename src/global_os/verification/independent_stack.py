"""Independent multi-method verification stack (GOS-I10 / GOS-I16).

Same model / same family retry is never independent. Consensus across
distinct diversity axes is required for tier ≥ INDEPENDENT.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from global_os.verification.diversity import VALID_FACTORS, assess_diversity

if TYPE_CHECKING:
    from global_os.verification.router import VerificationOutcome, VerificationTier

MethodRunner = Callable[[dict[str, Any]], "MethodResult"]

# Mirror VerificationTier.INDEPENDENT without importing router (cycle break).
_INDEPENDENT_TIER = 2


@dataclass(frozen=True)
class MethodResult:
    method_id: str
    passed: bool
    details: dict[str, Any]


@dataclass(frozen=True)
class MethodSpec:
    method_id: str
    family: str
    diversity_axis: str
    run: MethodRunner
    provider: str = ""
    model_family: str = ""


@dataclass(frozen=True)
class StackOutcome:
    passed: bool
    consensus: str
    diversity_factors: tuple[str, ...]
    method_results: tuple[MethodResult, ...]
    details: dict[str, Any]

    def as_verification_outcome(self, *, tier: VerificationTier) -> VerificationOutcome:
        from global_os.verification.router import VerificationOutcome as VO

        return VO(
            protocol="independent_multi_method",
            tier=tier,
            passed=self.passed,
            details={
                "consensus": self.consensus,
                "methods": [
                    {
                        "method_id": r.method_id,
                        "passed": r.passed,
                        "details": r.details,
                    }
                    for r in self.method_results
                ],
                **self.details,
            },
            diversity_factors=self.diversity_factors,
        )


def _axes_independent(methods: Sequence[MethodSpec]) -> tuple[bool, str, tuple[str, ...]]:
    axes = tuple(m.diversity_axis for m in methods)
    assessment = assess_diversity(axes)
    if not assessment.independent:
        return False, assessment.reason, assessment.factors
    distinct = frozenset(assessment.factors)
    if len(distinct) < 2:
        return (
            False,
            "independent tier requires ≥2 distinct diversity axes (GOS-I10)",
            assessment.factors,
        )
    return True, "ok", assessment.factors


def _llm_self_certifying(methods: Sequence[MethodSpec]) -> bool:
    """True when every method is an LLM judge from the same model family."""
    if not methods:
        return True
    if any(m.family != "llm_judge" for m in methods):
        return False
    families = {m.model_family or m.provider or m.method_id for m in methods}
    return len(families) <= 1


class IndependentVerificationStack:
    """Run multiple verifier methods and require diversity + consensus."""

    def __init__(self, methods: Sequence[MethodSpec]) -> None:
        if not methods:
            raise ValueError("IndependentVerificationStack requires ≥1 method")
        for m in methods:
            if m.diversity_axis not in VALID_FACTORS:
                raise ValueError(
                    f"method {m.method_id!r} has unrecognized diversity_axis "
                    f"{m.diversity_axis!r}"
                )
        self._methods = tuple(methods)

    @property
    def methods(self) -> tuple[MethodSpec, ...]:
        return self._methods

    def verify(self, payload: dict[str, Any], *, required_tier: int) -> StackOutcome:
        if required_tier >= _INDEPENDENT_TIER:
            if len(self._methods) < 2:
                return StackOutcome(
                    passed=False,
                    consensus="insufficient_diversity",
                    diversity_factors=(),
                    method_results=(),
                    details={
                        "reason": "independent tier requires ≥2 methods (GOS-I10)",
                    },
                )
            if _llm_self_certifying(self._methods):
                return StackOutcome(
                    passed=False,
                    consensus="insufficient_diversity",
                    diversity_factors=tuple(m.diversity_axis for m in self._methods),
                    method_results=(),
                    details={
                        "reason": "same model/family LLM judges are not independent (GOS-I10)",
                    },
                )
            ok, reason, factors = _axes_independent(self._methods)
            if not ok:
                return StackOutcome(
                    passed=False,
                    consensus="insufficient_diversity",
                    diversity_factors=factors,
                    method_results=(),
                    details={"reason": reason},
                )

        results: list[MethodResult] = []
        for method in self._methods:
            result = method.run(payload)
            if result.method_id != method.method_id:
                result = MethodResult(
                    method_id=method.method_id,
                    passed=result.passed,
                    details=result.details,
                )
            results.append(result)

        passes = [r.passed for r in results]
        if all(passes):
            consensus = "unanimous_pass"
            passed = True
        elif not any(passes):
            consensus = "unanimous_fail"
            passed = False
        else:
            consensus = "conflicted"  # GOS-I16
            passed = False

        return StackOutcome(
            passed=passed,
            consensus=consensus,
            diversity_factors=tuple(dict.fromkeys(m.diversity_axis for m in self._methods)),
            method_results=tuple(results),
            details={"required_tier": required_tier},
        )


def _equality_method(payload: dict[str, Any]) -> MethodResult:
    expected = payload.get("expected")
    actual = payload.get("actual")
    return MethodResult(
        method_id="equality",
        passed=expected == actual,
        details={"expected": expected, "actual": actual, "check": "equality"},
    )


def _digest_method(payload: dict[str, Any]) -> MethodResult:
    """Different algorithm: compare digests of canonicalized values."""
    expected = payload.get("expected")
    actual = payload.get("actual")

    def _digest(value: object) -> str:
        raw = repr(value).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    exp_d = _digest(expected)
    act_d = _digest(actual)
    return MethodResult(
        method_id="digest_recompute",
        passed=exp_d == act_d,
        details={"expected_digest": exp_d, "actual_digest": act_d, "check": "sha256_repr"},
    )


def numeric_independent_stack() -> IndependentVerificationStack:
    """Built-in dual deterministic stack for numeric claims (no LLM)."""
    return IndependentVerificationStack(
        (
            MethodSpec(
                method_id="equality",
                family="deterministic",
                diversity_axis="deterministic_recompute",
                run=_equality_method,
            ),
            MethodSpec(
                method_id="digest_recompute",
                family="deterministic",
                diversity_axis="different_algorithm",
                run=_digest_method,
            ),
        )
    )
