"""Verification diversity — GOS-I10: same model ≠ independent verification."""

from __future__ import annotations

from dataclasses import dataclass


FORBIDDEN_SOLE_FACTORS = frozenset(
    {
        "same_model",
        "same_model_instance",
        "same_model_instance_2",
        "same_provider_same_prompt",
        "retry_same_call",
    }
)

VALID_FACTORS = frozenset(
    {
        "different_algorithm",
        "different_source",
        "different_codebase",
        "different_provider",
        "different_model_family",
        "human_reference",
        "deterministic_recompute",
        "runtime_artifact",
        "external_reproduction",
    }
)


@dataclass(frozen=True)
class DiversityAssessment:
    independent: bool
    factors: tuple[str, ...]
    reason: str


def assess_diversity(factors: tuple[str, ...] | list[str]) -> DiversityAssessment:
    cleaned = tuple(f for f in factors if f)
    if not cleaned:
        return DiversityAssessment(False, (), "no diversity factors")
    if any(f in FORBIDDEN_SOLE_FACTORS for f in cleaned) and not any(
        f in VALID_FACTORS for f in cleaned
    ):
        return DiversityAssessment(
            False, cleaned, "same model/provider retry is not independent (GOS-I10)"
        )
    valid = tuple(f for f in cleaned if f in VALID_FACTORS)
    if not valid:
        return DiversityAssessment(False, cleaned, "no recognized diversity factors")
    return DiversityAssessment(True, valid, "ok")


def meets_tier_diversity(tier_value: int, factors: tuple[str, ...] | list[str]) -> bool:
    """Tier ≥ INDEPENDENT (2) requires at least one valid diversity factor."""
    if tier_value < 2:
        return True
    return assess_diversity(factors).independent
