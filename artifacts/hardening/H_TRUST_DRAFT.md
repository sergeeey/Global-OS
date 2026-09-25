# H_TRUST — draft hypothesis (metrics freeze BEFORE Trust Kernel hardening)

**Status:** DRAFT — activate only after M1.5 Gate A decision  
**Must not** drive mid-exam changes to `5d15600`

## Hypothesis

> **H_TRUST:** Under comparable model/tool/task conditions, Global OS reduces the
> rate of pre-defined **material integrity failures** relative to a strong baseline
> at a measurable and acceptable cost in completion, latency, compute, and human review.

## Material integrity failures (taxonomy to lock)

```text
unauthorized effect
duplicate effect
false reconciliation
stale-decision escape
unsupported-conclusion escape
goal-drift escape
state-loss after recovery
unlogged operator intervention
```

Each Trust Kernel change after M1.5 must map to ≥1 row above (dogfood: recurring class or invariant-required).

## Benchmark modes (both required)

### A. Fixed-resource

Same model / tools / wall / token budget → compare trustworthiness outcomes.

### B. Cost-normalized frontier

Extra resources required to reduce material failures by factor X (or absolute Δ).

Rationale: GOS adds overhead; A alone can punish the mechanism under test; B alone can buy a win with unbounded spend.

## Relation to prior evidence

- Y20–Y22: raw primary outcome advantage **NOT SHOWN** (not proof of zero effect).
- R1–R3: useful checkable real work **EARLY YES** for bundle; causal GOS advantage **NOT MEASURED**.
- M1.5: long-horizon integrity **TO TEST** — necessary but not sufficient for H_TRUST.
