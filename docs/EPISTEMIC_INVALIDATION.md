# EPISTEMIC_INVALIDATION.md — Transition contracts

## Principle

$$
\text{implemented approximation} \neq \text{fulfilled contract}
$$

## Runtime chain (GOS-I12)

```text
Source stale/invalid
  → Observation STALE/INVALIDATED
  → Claim STALE / CONTRADICTED / NEEDS_REVIEW
  → Belief STALE
  → Model STALE
  → Forecast STALE
  → Decision NEEDS_REVIEW
  → Commitment NEEDS_REVIEW (if depends_on claims)
```

Evidence: `tests/test_epistemic.py`, `tests/test_observation_belief.py`.

## GOS-I21 / GOS-I22 reminder

- Reasoning traces ≠ evidence (cannot create SYSTEM_TRUSTED Observation).
- Execution/tool traces = evidence candidates until Verification assigns epistemic status.

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

## Implementation evidence

| Transition | State |
| ---------- | ----- |
| evidence → claim STALE | RUNTIME_VERIFIED_LOCAL |
| observation → belief → claim | RUNTIME_VERIFIED_LOCAL |
| claim → model → forecast → decision → commitment | RUNTIME_VERIFIED_LOCAL |
| reasoning_trace → evidence | FORBIDDEN (GOS-I21) |
| event replay status projection | RUNTIME_VERIFIED_LOCAL |
