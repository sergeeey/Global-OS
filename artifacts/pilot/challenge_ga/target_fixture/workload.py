"""Sealed Challenge-GA target fixture — optimize without breaking the public API.

Interface freeze (binding):
  process_items(items: list[int]) -> int
  last_ops() -> int

Naive reference is O(n²). Challenge WIN requires correct results on sealed
vectors with ops ≤ sealed budget (see TARGET.md / LOCK.json).
"""

from __future__ import annotations

_OPS = 0


def last_ops() -> int:
    """Instrumentation for scoring — not part of the product API under test."""
    return _OPS


def process_items(items: list[int]) -> int:
    """Return a checksum over pairwise combinations (naive O(n²) reference)."""
    global _OPS
    _OPS = 0
    total = 0
    n = len(items)
    for i in range(n):
        for j in range(n):
            _OPS += 1
            total += (items[i] + items[j]) % 97
    return total
