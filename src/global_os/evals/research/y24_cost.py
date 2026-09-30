"""Y24 cost-matching ledger helpers (weights locked with prereg)."""

from __future__ import annotations

from typing import Any

# Locked with artifacts/y24/Y24-COST-ACCOUNTING.md
WEIGHTS = {
    "llm_cost_tokens": 1.0,
    "tool_calls": 50.0,
    "human_interventions": 5000.0,
    "latency_ms": 0.001,
    "verification_calls": 100.0,
    "recovery_overhead_seconds": 10.0,
}

COST_RATIO_MAX = 1.25

LEDGER_FIELDS = (
    "model_tokens_in",
    "model_tokens_out",
    "llm_cost_tokens",
    "tool_calls",
    "verification_calls",
    "wall_seconds",
    "latency_ms",
    "human_interventions",
    "retry_count",
    "recovery_overhead_seconds",
    "escalations",
)


def verification_cost(ledger: dict[str, Any]) -> float:
    missing = [k for k in WEIGHTS if k not in ledger]
    if missing:
        raise ValueError(f"ledger missing cost fields: {missing}")
    total = 0.0
    for key, weight in WEIGHTS.items():
        total += weight * float(ledger[key])
    return total


def cost_match_ok(
    cost_a: float,
    cost_c: float,
    *,
    ratio_max: float = COST_RATIO_MAX,
) -> bool:
    if cost_a < 0 or cost_c < 0:
        raise ValueError("costs must be non-negative")
    if cost_a == 0:
        return cost_c == 0
    return cost_c <= cost_a * ratio_max
