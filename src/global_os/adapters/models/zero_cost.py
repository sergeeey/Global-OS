"""GOS_ZERO_COST_MODE — prefer free endpoints; deny paid spend without override."""

from __future__ import annotations

import os
from typing import Any

from global_os.adapters.models.base import ModelProviderError


def zero_cost_mode_enabled() -> bool:
    return os.environ.get("GOS_ZERO_COST_MODE", "") == "1"


def scientific_eval_mode() -> bool:
    return os.environ.get("GOS_SCIENTIFIC_EVAL", "") == "1"


def assert_zero_cost_allowed(
    *,
    cost_usd: float | None,
    free_tier: bool,
    data_classification: str = "public",
    training_possible: bool = False,
    paid_override: bool = False,
) -> None:
    """Fail closed when zero-cost mode forbids the call."""
    if data_classification == "confidential" and training_possible:
        raise ModelProviderError(
            "data_policy DENY: confidential content forbidden on training-possible free provider"
        )
    if not zero_cost_mode_enabled():
        return
    if paid_override and os.environ.get("GOS_ALLOW_PAID", "") == "1":
        return
    if not free_tier:
        raise ModelProviderError("GOS_ZERO_COST_MODE=1: paid endpoint DENY")
    if cost_usd is not None and cost_usd > 0:
        raise ModelProviderError(
            f"GOS_ZERO_COST_MODE=1: cost_usd={cost_usd} > 0 DENY (set GOS_ALLOW_PAID=1 to override)"
        )


def prefer_free_descriptor(descriptors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort capability descriptors: free/zero cost first when zero-cost mode on."""
    if not zero_cost_mode_enabled():
        return list(descriptors)
    return sorted(
        descriptors,
        key=lambda d: (
            0 if float(d.get("cost_usd_per_unit") or 0) == 0 else 1,
            0 if d.get("privacy", {}).get("free_tier") else 1,
            d.get("id", ""),
        ),
    )
