# EPISTEMIC_INVALIDATION.md — Transition contracts

## Principle

$$
\text{implemented approximation} \neq \text{fulfilled contract}
$$

Current runtime seed: `evidence INVALIDATED → dependent ACTIVE claim → STALE`.

Target chain (CONTRACTED until graph runtime lands):

```text
Source stale/invalid
  → Observation STALE/INVALIDATED
  → Claim STALE / CONTRADICTED
  → Assumption STALE
  → Belief STALE / CONFLICTED
  → Hypothesis needs_review | KILLED
  → Model STALE
  → Forecast STALE
  → Decision NEEDS_REVIEW
  → Commitment NEEDS_REVIEW (if depends_on claims)
```

## GOS-I21 reminder

Reasoning traces, chain-of-thought, and model self-report are **not** evidence and must not create Observation nodes with `trust_label=SYSTEM_TRUSTED`.

## Allowed edges (contract)

```text
Observation --supports--> Claim
Observation --derived_from--> Source/Artifact
Belief --derived_from--> Observation*
Claim --supported_by--> Evidence
Evidence --invalidates--> Claim (via engine)
Hypothesis --assumes--> Assumption
Forecast --depends_on--> Model
Decision --depends_on--> Claim|Forecast
Commitment --depends_on--> Claim
```

## Current implementation evidence

| Transition | State |
| ---------- | ----- |
| evidence → claim STALE | RUNTIME_VERIFIED_LOCAL |
| observation → belief | CONTRACTED (schemas only) |
| recursive model/forecast/decision | CONTRACTED |
| reasoning_trace → evidence | FORBIDDEN (GOS-I21) |
