# Y25 — Isolation gate (LOCKED)

**Status:** `ISOLATION_GATE_LOCKED`  
**Protocol:** `Y25-MV-v1`

## Rule

W1 (WITH_MEMORY) builders and memory-seed pipelines must **not** access sealed
holdout labels/outcomes before execution unseal.

Allowed before unseal:

- public blind refs
- DEV first-encounter incidents for memory seeding
- schemas / prereg / cost formula

Forbidden before unseal:

- sealed holdout failure_class / pair outcomes
- tuning memory retrieval using holdout arm results

## Attestation

See `ISOLATION_ATTESTATION.md` — required before unseal execution.
