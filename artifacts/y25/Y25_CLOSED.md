# Y25 — CLOSED

**Status:** `CAMPAIGN_CLOSED`  
**Closed (UTC):** 2026-10-01  
**Closure type:** scientific (protocol-terminal) — **no Y25-F2**

## Terminal record

```text
CAMPAIGN_CLOSED
decision      REJECT
fidelity      HEURISTIC_HARNESS_v1
primary       median cost ratio ≈ 0.80
MCID          ≤ 0.60 required
memory value  NOT SHOWN at preregistered strength
TK            UNCHANGED
```

## Meaning (only this)

W1 (with memory) showed roughly **~20%** median cost reduction vs W0, but the
preregistered KEEP gate required ≤ **0.60** (~40% reduction). Therefore the
**strong** H_memory effect was **not** confirmed under `HEURISTIC_HARNESS_v1`.

```text
REJECT ≠ «память совершенно бесполезна»
REJECT  = «заявленный сильный эффект не подтверждён»
```

## Methodological cleanliness (keep)

- prereg SHA frozen **before** corpus familiarity
- ≥24 cross-repo pairs; holdout N=13
- seal → attest → execution
- no post-unseal N expansion
- thresholds not moved
- Y24 not rescued by this result
- Trust Kernel untouched

## Explicitly forbidden after close

```text
0.60 → 0.85
добавить ещё N
подкрутить memory
выбрать другие failure classes
live LLM "чтобы вдруг получилось"
Y25-F2
ThymusKernel / ImmuneMemoryService / AdaptiveVerifierMegaLayer
```

Those would be a **new** hypothesis / new experiment — not a continuation of Y25.

## Joint lesson with Y24

| Campaign | Cellular analogy | Result under protocol |
|----------|------------------|------------------------|
| Y24 | adaptive “immune” verifier | Adaptive-C advantage NOT SHOWN |
| Y25 | “immune memory” | Strong memory value NOT SHOWN (~20% ≠ ≥40%) |

Biology gave useful hypotheses; experiments did **not** justify promoting them
into architecture yet. **Strong evidence: absent.**
