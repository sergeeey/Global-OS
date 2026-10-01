"""Y25 pair_cost accounting (locked weights)."""

from __future__ import annotations

from typing import Any

WEIGHTS = {
    "llm_cost_tokens": 1.0,
    "tool_calls": 50.0,
    "human_interventions": 5000.0,
    "latency_ms": 0.001,
    "verification_calls": 100.0,
    "recovery_overhead_seconds": 10.0,
    "time_to_diagnosis_s": 1.0,
}

MEMORY_COST_RATIO_MAX = 0.6


def pair_cost(ledger: dict[str, Any]) -> float:
    total = 0.0
    for key, weight in WEIGHTS.items():
        total += weight * float(ledger.get(key) or 0)
    return total


def memory_cost_ratio_ok(
    cost_w0_unseen: float,
    cost_w1_unseen: float,
    *,
    ratio_max: float = MEMORY_COST_RATIO_MAX,
) -> bool:
    if cost_w0_unseen <= 0:
        return False
    return (cost_w1_unseen / cost_w0_unseen) <= ratio_max
