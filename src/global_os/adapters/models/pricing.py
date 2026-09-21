"""Approximate USD cost for model.invoked event trail (not billing truth)."""

from __future__ import annotations

# (input_per_1m, output_per_1m) USD
_RATES: dict[tuple[str, str], tuple[float, float]] = {
    ("openai", "gpt-4o-mini"): (0.15, 0.60),
    ("openai", "gpt-4o"): (2.50, 10.00),
    ("anthropic", "claude-3-5-haiku-latest"): (0.80, 4.00),
    ("anthropic", "claude-3-5-sonnet-latest"): (3.00, 15.00),
    ("anthropic", "claude-3-haiku-20240307"): (0.25, 1.25),
}


def estimate_cost_usd(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float | None:
    """Return estimated USD or None when rate unknown (still record tokens/latency)."""
    key = (provider.lower(), model.lower())
    rates = _RATES.get(key)
    if rates is None:
        # prefix match for versioned model ids
        for (p, m), r in _RATES.items():
            if p == provider.lower() and model.lower().startswith(m.split("-20")[0]):
                rates = r
                break
    if rates is None:
        return None
    inp, out = rates
    return round((input_tokens / 1_000_000.0) * inp + (output_tokens / 1_000_000.0) * out, 8)
