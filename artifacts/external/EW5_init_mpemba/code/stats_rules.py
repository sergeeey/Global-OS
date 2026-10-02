"""Locked statistical helpers for M-EXT5 (internally consistent)."""

from __future__ import annotations

from math import ceil, comb

PRIMARY_N = 20
PRIMARY_MIN_WINS = 15  # Bin(20,0.5) one-sided: P(X>=15)≈0.0207 < 0.05; P(X>=14)≈0.0577


def one_sided_binom_p(wins: int, n: int, p0: float = 0.5) -> float:
    """P(X >= wins) under Bin(n, p0). Exact for p0=0.5."""
    if not 0 <= wins <= n:
        raise ValueError("wins out of range")
    if abs(p0 - 0.5) < 1e-12:
        return sum(comb(n, k) for k in range(wins, n + 1)) / (2**n)
    s = 0.0
    for k in range(wins, n + 1):
        s += comb(n, k) * (p0**k) * ((1 - p0) ** (n - k))
    return s


def decide_effect(n_wins: int, n_valid: int) -> str:
    """H_EFFECT primary decision under locked rule."""
    if n_valid < 16:
        return "INCONCLUSIVE"
    need = int(ceil(PRIMARY_MIN_WINS * n_valid / PRIMARY_N))
    p = one_sided_binom_p(n_wins, n_valid)
    if n_wins >= need and p < 0.05:
        return "SUPPORTED_WITHIN_SCOPE"
    # For n=20: need=15 → REJECTED if wins <= 12; 13–14 INCONCLUSIVE
    if n_wins <= need - 3:
        return "REJECTED"
    return "INCONCLUSIVE"


def decide_fisher(effect: str, hot_gn_gt_cold_count: int, n_valid: int) -> str:
    """H_FISHER: only meaningful if effect supported; else REJECTED/INCONCLUSIVE."""
    if effect != "SUPPORTED_WITHIN_SCOPE":
        return "INCONCLUSIVE" if effect == "INCONCLUSIVE" else "REJECTED"
    if n_valid < 16:
        return "INCONCLUSIVE"
    need = int(ceil(PRIMARY_MIN_WINS * n_valid / PRIMARY_N))
    p = one_sided_binom_p(hot_gn_gt_cold_count, n_valid)
    if hot_gn_gt_cold_count >= need and p < 0.05:
        return "SUPPORTED_WITHIN_SCOPE"
    if hot_gn_gt_cold_count <= need - 3:
        return "REJECTED"
    return "INCONCLUSIVE"
