# GLOBAL-OS-CAUSAL-ROOT-CAUSE-1

## Root cause — OBSERVED

`run_repo_audit()` called `scan_repo_structure()`, which called `Path.resolve()` and
`root.rglob("*")` without checking that the target exists and is a directory.
For a missing path, `rglob` returned no files, so the tool produced a normal report
with `file_count=0` and synthetic findings (`f_missing_constitution`, `f_no_tests`,
`f_invariants_missing`, `f_provider_boundary_clean`).

`verify_repo_audit_report()` then accepted the report because it checked only
`read_only`, `modified_target`, non-empty findings, and `scan` shape. The preprod
handler returned `ToolResult(True, report)`, the Completion Gate marked `sc_01`
met, and delivery returned `SUCCEEDED`.

First failing boundary: `scan_repo_structure()` — a missing target became an empty
normal scan. The weak verifier was secondary; no runtime error existed to lose.

## Fix

- `scan_repo_structure()` now raises `FileNotFoundError` for a missing target and
  `NotADirectoryError` for a file target before scanning.
- `_gateway_observe_step()` catches those two input errors and returns a state with
  `effect_receipts=[]`, `artifact_digest=None`, `observe_block="invalid_target"`,
  and `artifact_verify.ok=False`. The normal Completion Gate then reports
  `UNKNOWN` and delivery is `INCONCLUSIVE`.
- No duplicate check was added to the verifier; `repo.audit` remains the single
  input-validation boundary.

## Tests

- `tests/test_repo_audit.py`: missing target and file target raise.
- `tests/test_preprod_supervised_mission_e2e.py`: missing/file target is
  `INCONCLUSIVE`, no criterion met; valid target success tests unchanged.
- Targeted: 24 passed.
- Full suite: 463 passed, 9 failed, 14 skipped. The same 9 failures reproduce on
  baseline `origin/main` and are pre-existing frozen-pack/Rust-environment
  failures, not caused by this change.

## Pilot

Same six-task oracle as PARETO-PROGRESS-1:

- before origin preprod: 5/6 correct, 1 false SUCCESS, 7.70 s, 0 model cycles;
- after fixed preprod: 6/6 correct, 0 false SUCCESS, 7.78 s, 0 model cycles;
- candidate terminal: 6/6 correct, 0 false SUCCESS, 7.89 s, 12 model cycles.

The fixed run counts successful goal achievement and correct refusal separately:
five valid targets SUCCEEDED; one missing target was correctly rejected as
INCONCLUSIVE.

Limitations: the six-task pilot is in-house and not independent; it covers only
read-only audit; the preprod refusal is INCONCLUSIVE rather than FAILED.
