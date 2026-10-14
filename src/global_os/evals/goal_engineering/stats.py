"""Bootstrap confidence intervals — no parametric assumptions required."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class Interval:
    estimate: float
    low: float
    high: float
    n: int
    level: float


def _xorshift(seed: int) -> int:
    x = seed & 0xFFFFFFFF
    x ^= (x << 13) & 0xFFFFFFFF
    x ^= x >> 17
    x ^= (x << 5) & 0xFFFFFFFF
    return x & 0xFFFFFFFF


def mean(xs: Sequence[float]) -> float:
    if not xs:
        return float("nan")
    return sum(xs) / len(xs)


def bootstrap_mean_ci(
    xs: Sequence[float],
    *,
    n_boot: int = 2000,
    seed: int = 2907,
    level: float = 0.90,
) -> Interval:
    n = len(xs)
    if n == 0:
        return Interval(float("nan"), float("nan"), float("nan"), 0, level)
    est = mean(xs)
    if n == 1:
        return Interval(est, est, est, 1, level)
    samples: list[float] = []
    state = seed & 0xFFFFFFFF
    for _ in range(n_boot):
        acc = 0.0
        for _j in range(n):
            state = _xorshift(state)
            acc += xs[state % n]
        samples.append(acc / n)
    samples.sort()
    alpha = 1.0 - level
    lo_i = int(alpha / 2 * (n_boot - 1))
    hi_i = int((1 - alpha / 2) * (n_boot - 1))
    return Interval(est, samples[lo_i], samples[hi_i], n, level)


def bootstrap_diff_ci(
    a: Sequence[float],
    b: Sequence[float],
    *,
    n_boot: int = 2000,
    seed: int = 2907,
    level: float = 0.90,
) -> Interval:
    """CI for mean(a) - mean(b)."""
    n = min(len(a), len(b))
    if n == 0:
        return Interval(float("nan"), float("nan"), float("nan"), 0, level)
    aa = list(a[:n])
    bb = list(b[:n])
    est = mean(aa) - mean(bb)
    samples: list[float] = []
    state = seed & 0xFFFFFFFF
    for _ in range(n_boot):
        sa = 0.0
        sb = 0.0
        for _j in range(n):
            state = _xorshift(state)
            sa += aa[state % n]
            state = _xorshift(state)
            sb += bb[state % n]
        samples.append(sa / n - sb / n)
    samples.sort()
    alpha = 1.0 - level
    lo_i = int(alpha / 2 * (n_boot - 1))
    hi_i = int((1 - alpha / 2) * (n_boot - 1))
    return Interval(est, samples[lo_i], samples[hi_i], n, level)
