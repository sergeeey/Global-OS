# GLOBAL-OS-MINIMAL-TERMINAL-PORT-1

## Implemented

One `_resolve_terminal()` used by both `status_mission()` and
`deliver_mission()`.

Checks only data present in this runtime:

- `control.status`;
- existence and `terminal_status` of `delivery.json`;
- `state.completion`;
- `state.artifact_digest` and `artifacts/sha256/<digest>`;
- `state.artifact_verify`;
- non-empty `state.effect_receipts`.

## Behaviour

- valid SUCCEEDED -> SUCCEEDED
- valid FAILED -> FAILED
- normal PAUSED without delivery -> PAUSED; deliver still raises
  `delivery not ready`
- control SUCCEEDED + missing delivery -> INCONCLUSIVE, structured refusal
- delivery/control/completion mismatch -> INCONCLUSIVE
- missing/tampered artifact at success -> INCONCLUSIVE
- empty receipts or artifact_verify=false at success -> INCONCLUSIVE

Additive fields: `control_status`, `accepted`, `delivery_integrity`.

## Excluded

- cascade trace / workflow;
- falsifiers;
- substrate health;
- tool catalog;
- per-receipt `tool_id`/`artifact_digest` binding;
- new state-machine steps.

Per-receipt binding is a residual because origin receipts do not contain those
fields. Cascade trace is not applicable because origin has no cascade state.

## Tests

```text
tests/test_terminal_minimal.py  9 passed
targeted A/e2e               33 passed
full suite                   472 passed, 9 failed, 14 skipped
```

The same 9 pre-existing frozen-pack/Rust failures remain; no new failures.

## Commands

```powershell
$env:PYTHONPATH = "C:\gos_integration_1\src;C:\gos_integration_1"
python -m pytest -q tests/test_terminal_minimal.py
python -m pytest -q
```
