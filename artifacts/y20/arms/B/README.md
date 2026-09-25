# Arm B — same model + Global OS

**Status:** NOT RUN  
**Prereg boundary:** `278c10d`

## What this arm is

Same model pin as Arm A, plus Global OS structure:

- Goal Contract
- durable research state
- falsification / verification loop
- autonomous continuation
- stop conditions

Same public data, same budgets, same right to write code.

## Inputs

- Same `artifacts/y20/public/` pack (hash must match CURRENT_STATE)
- Y20 program + GOS durable state pattern (as in Y19 campaign style)
- **Forbidden:** sealed GT; reading Arm A submission/results; extra compute beyond caps

## Outputs (immutable after stop)

- `submission.json`
- `process_log.json`
- durable research handoff files under `workdir/`

## Sequence rule

Start only after Arm A artifacts are immutable.  
Unseal only after this arm is frozen.
