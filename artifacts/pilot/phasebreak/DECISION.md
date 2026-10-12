# DECISION — PILOT-PB-CLAIMS-v1

**Pilot:** PhaseBreak-2026 claims audit  
**Tip:** `fd1e55c5fad7bfdcb88dd844ccafe95275bebddd`  
**GOS tip at start:** `3e4de13` (PR #17 merged)  
**Status:** `TERMINAL`  
**Date (UTC):** 2026-10-12

## Terminal verdict

```text
PRODUCT_MATURITY_CLAIM (production-usable science product) = REJECTED
HEADLINE_FINANCE_METRICS_vs_STORED_JSON                 = SUPPORTED
UNIVERSALITY_CONFIRMED                                  = REJECTED
README_COMMODITIES_RECALL_50%                           = REJECTED (stale; JSON=67%)
FORWARD_NIKKEI_NARRATIVE                                = INCONCLUSIVE (JSON vs failure doc)
GOS_vs_STRONG_AGENT_ADVANTAGE                           = NOT_MEASURED
```

## Hypotheses

| Id | Result |
|----|--------|
| H1 README metrics match stored JSON | **PARTIAL** — finance OK; commodities recall stale |
| H2 production-usable justified by crash/live | **REJECTED** — crash P=50% R≈23% |
| H3 universality confirmed | **REJECTED** — KS non-rejection / low power |
| H4 Nikkei consistent | **INCONCLUSIVE** |
| H5 headline P/R test-locked | **REJECTED** |

## What is useful independently of GOS

1. Errata already in `CORRECTIONS.md` are directionally correct (universality, fraud leakage, loose ablation).
2. Stored `benchmark_results.json` is a coherent numerical spine for finance/housing/ablation.
3. Highest-value next PhaseBreak hygiene (optional, out of scope unless requested):
   - fix README commodities recall 50%→67%
   - downgrade “production-usable” / `production-like` until crash eval or live P&L supports it
   - reconcile Nikkei forward JSON vs `NIKKEI_FAILURE_ANALYSIS.md`
   - add pytest asserts for official P/R floats (±ε)

## Interventions log

| # | Intervention | Why |
|---|--------------|-----|
| 0 | none intellectual coaching of PhaseBreak mid-run | contract forbids metric fishing |
| 1 | clone GitHub tip (not D:\ mount) | cloud has no Windows D: |
| 2 | re-derive numbers via Python JSON only | no full `reproduce.sh` (network/deps) |
| 3 | hygiene patch prepared; PhaseBreak push **403** | apply `PROPOSED_HYGIENE.patch` on `D:\PhaseBreak-2026` or open PR with your creds |

## Honesty

```text
implemented approximation ≠ fulfilled contract
stored benchmark ≠ live forward proof
KS p>0.05 ≠ universality
synthetic fraud/landslide ≠ real-world performance
pilot audit ≠ GOS PRODUCTION_PROVEN
```

## Artifacts

- `GOAL_CONTRACT.md`
- `CLAIM_LEDGER.json`
- `VERIFIED_NUMBERS.json`
- `DECISION.md` (this file)
- `INTERVENTIONS.json`
- `README.md`
