# Arm A — strong-agent baseline

**Status:** NOT RUN  
**Prereg boundary:** `278c10d`

## What this arm is

Strong Codex/Claude + ordinary workspace + filesystem/python.  
Full right to explore and write code.  
**No** Goal Contract / Epistemic / durable GOS research loop / GOS stop contract.

Do **not** cripple this arm. Equal model, data, and budgets vs Arm B.

## Inputs

- Copy or mount `artifacts/y20/public/` only
- Read `artifacts/y20/Y20-PREREG.md` task description (not sealed/)
- **Forbidden:** `artifacts/y20/sealed/`, generator internals for answers, operator hypothesis dispatch

## Outputs (immutable after stop)

- `submission.json` (schema in prereg)
- `process_log.json` (see `../process_log.schema.json`)
- Optional workdir notebooks/scripts under `workdir/`

## Sequence rule

Complete Arm A and freeze this directory **before** starting Arm B.  
Do not unseal until Arm B is also frozen.
