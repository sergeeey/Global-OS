# H_TRUST — hypothesis (metrics FROZEN; Trust Kernel NOT built)

**Status:** `METRICS_FROZEN` — SAFE_AUTONOMY_BENCHMARK-v1 locked  
**Activated after:** M1.5 `CLOSED_SCOPE_LIMITED` (`M15_DECISION.md`)  
**Benchmark:** `artifacts/hardening/SAFE_AUTONOMY_BENCHMARK_V1.md` (+ `.json`)  
**Must not** reopen LH-COGNITIVE 48h or patch exam SHA `7ab345e` for this hypothesis

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
- Benchmark freeze: **SAFE_AUTONOMY_BENCHMARK-v1** (`METRICS_FROZEN`; arms not started)
- MCID: **SET_BY_VARIANCE_PILOT_v1** (mier=0.04 / ssr=0.18 / eps=0.02; synthetic sandbox ≠ T1)
- Metric module: `src/global_os/evals/trust/safe_autonomy_metrics.py`
- First experiment: **T1 SAFE_AUTONOMY_ENVELOPE** (A strong agent / B current GOS / C GOS+assurance)
- Primary metrics: MIER + SSR; falsifier = utility/attention tax unacceptable or C≈B
- Must stay **deterministic/stateful first**; LLM monitor never sole oracle
- **Do not implement Mission Assurance in core** until T1 KEEP
