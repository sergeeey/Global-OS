# EPISTEMIC_MODEL.md

## Separation (GOS-I07)

Typed nodes — never a single generic memory blob:

```text
Source · Artifact · Observation · Claim · Assumption · Hypothesis · Model
Forecast · Decision · Commitment · Experiment · Verification · Defeater · Unknown
```

Edges: supports, contradicts, derived_from, depends_on, assumes, observed_in, predicts, falsifies, invalidates, supersedes, verified_by, generated_by, used_in.

## Bitemporal fields

`recorded_at`, `known_at`, `valid_from`, `valid_until`, `observed_at`, `verified_at`.

Distinguish: when the world was thus vs when Global OS learned it.

## Evidence status (not boolean)

```text
UNVERIFIED → ATTRIBUTED → SOURCE_RESOLVED → SOURCE_CONTENT_VERIFIED
→ DERIVED → RUNTIME_VERIFIED → INDEPENDENTLY_VERIFIED → EXTERNALLY_REPRODUCED
(+ CONTRADICTED | STALE | INVALIDATED)
```

## Confidence

- Calibrated probability — only with calibration method  
- Epistemic confidence: LOW | MEDIUM | HIGH | VERY_HIGH + `confidence_basis`

## Invalidation

Machine propagation: source → claim → assumption → forecast → decision needs_review.

## Hypothesis lifecycle (Y-17)

PROPOSED → ACTIVE → SUPPORTED | KILLED | INCONCLUSIVE → CLOSED  

Required: kill_criteria, alternative_explanations, reopen_conditions.  
`null_results` are first-class.

## Trust labels / taint

`SYSTEM_TRUSTED` | `USER_TRUSTED` | `ORG_TRUSTED` | `EXTERNAL_UNTRUSTED` | `MODEL_GENERATED` | `DERIVED`  

External untrusted data: usable as data; never expands authority, mutates Goal, fetches secrets, or drives privileged tools.
