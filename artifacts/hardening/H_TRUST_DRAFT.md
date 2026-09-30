# H_TRUST — hypothesis (metrics FROZEN; Trust Kernel NOT built)

**Status:** `REJECTED_IN_TESTED_SCOPE` — T1 REJECT under `DETERMINISTIC_FAULT_MISSIONS_v1`  
**Activated after:** M1.5 `CLOSED_SCOPE_LIMITED` (`M15_DECISION.md`)  
**Benchmark:** `artifacts/hardening/SAFE_AUTONOMY_BENCHMARK_V1.md` (+ `.json`)  
**Decision:** `artifacts/safe_autonomy_t1/T1_DECISION.md` · ADR-0011  
**Must not** reopen LH-COGNITIVE 48h, rewrite MCID, or promote Mission Assurance after REJECT

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
- M1.5: long-horizon integrity **SHOWN** within LH-COGNITIVE-v1 scope — necessary but not sufficient for H_TRUST.

## Leading mechanism candidate (post-M1.5 — not implemented)

**Mission-Level Runtime Assurance + Bounded Recovery** (“Cognitive Simplex” = experiment label).

- Plan: `artifacts/hardening/NEXT_MECHANISM_MISSION_ASSURANCE.md`
- Benchmark freeze: **SAFE_AUTONOMY_BENCHMARK-v1** (`METRICS_FROZEN`; arms complete)
- MCID: **SET_BY_VARIANCE_PILOT_v1** (mier=0.04 / ssr=0.18 / eps=0.02) — unchanged after T1
- T1 result: **REJECT** — MIER_C=0 vs A=0.9/B=0.8 but `verifier_tax_2_0_completion`
- **Do not implement Mission Assurance in core** after REJECT (ADR-0011)
