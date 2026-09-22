# DEVELOPMENT_RULES_DOGFOOD.md — empirical rules from hardening missions

**Status:** Binding for dogfood phase (not a new subsystem — process constraint)

## Subsystem creation gate

A new subsystem is created ONLY if:

1. an invariant (CONSTITUTION / SPEC) requires it, OR
2. the **same failure class** appeared in **≥2 independent real missions**
   and a minimal fix is insufficient without a reusable primitive.

Forbidden: creating a subsystem from a single aesthetic idea or one-off inconvenience.

## Continual improvement metric (aspirational, not claimed)

Holdout question for later:

> Does Global OS improve its future mission success / escaped-error rate after learning
> from past failure cases?

Not yet measured. Do not claim continual self-improvement until holdout missions show it.

## Temporal / forecasting protocol (Y17-5+)

For predictive missions:

- lock train / holdout split **before** any holdout compute
- declare competing baseline before fit
- kill criterion must require beating baseline on holdout
- post-cutoff / holdout information must not enter training
