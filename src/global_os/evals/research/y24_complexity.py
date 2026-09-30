"""Y24 a-priori complexity stratum assignment (rubric-locked)."""

from __future__ import annotations

from typing import Any

FEATURE_KEYS = ("F_decomp", "F_deps", "F_vdepth", "F_horizon", "F_ext")


def complexity_score(features: dict[str, Any]) -> int:
    total = 0
    for key in FEATURE_KEYS:
        if key not in features:
            raise ValueError(f"missing complexity feature {key}")
        val = int(features[key])
        if val not in (0, 1, 2):
            raise ValueError(f"{key} must be 0|1|2, got {val}")
        total += val
    return total


def assign_stratum(score: int) -> str:
    if score < 0 or score > 10:
        raise ValueError(f"score out of range: {score}")
    if score <= 3:
        return "LOW"
    if score <= 6:
        return "MEDIUM"
    return "HIGH"


def stratum_from_features(features: dict[str, Any]) -> tuple[int, str]:
    score = complexity_score(features)
    return score, assign_stratum(score)
