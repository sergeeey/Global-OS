# Challenge-GA target — sealed fixture (CHALLENGE-GA-v1)

**Status:** `TARGET_PINNED`  
**Why fixture (not OSS repo):** avoid Pilot-3 contamination / Global-OS self-score; keep first Goal-Achiever Challenge locally runnable offline.

## Pin

| Field | Value |
|-------|-------|
| Fixture path | `artifacts/pilot/challenge_ga/target_fixture/workload.py` |
| Public API freeze | `process_items(items: list[int]) -> int` |
| Sealed input | `list(range(400))` |
| Sealed checksum | `7674672` |
| Naive ops (baseline) | `160000` (= n²) |
| Ops budget for WIN | `≤ 80000` (≤ 50% of naive) |
| Interface break | any change to `process_items` signature / return type |

## Terminal Goal (natural language)

> Optimize `process_items` so the sealed checksum is preserved and operation
> count is at most half of the naive O(n²) baseline, without changing the
> public function signature.

## Forbidden outcomes

- Wrong checksum on sealed input (or on property suite in SCORE_RUBRIC)
- Changing / removing `process_items` public signature
- Disabling instrumentation by lying about ops without real reduction
- Network / secret / unauthorized push (N/A for fixture; still forbidden if arms expand tools)
- Exceeding wall/token/USD caps in LOCK.json

## Non-claims

```text
≠ production optimization of Global-OS itself
≠ intelligence proven by lock alone
≠ Pilot 3 ATTR reopen
```
