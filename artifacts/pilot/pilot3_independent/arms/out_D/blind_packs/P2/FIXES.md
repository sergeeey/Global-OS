# Proposed minimal fixes (regression-safe)

Applied and verified in `/tmp/pilot/p3-arm-A/tools/workflow-controller` for Pack evidence only.  
Patch: `REPRO/proposed_fixes.patch`  
Probe: `REPRO/test_pilot3_arm_a_regressions.py` (fail → pass).  
In-tree suite after fix: **55 passed** (`python3 -m unittest discover -s tests`).

## F1 — event log / artifact FAIL

1. `issue_runner.py`: emit `artifact gate {_status_verb(status)}` (align with security final reasons: `failed` / `blocked`).  
2. `event_log.py`: for single prior event, require `reason == f"artifact gate {_status_verb(status)}"`, allow both `fail` and `blocked`, and apply the same `blocked_reason` rules as the security path.

## F2 — `output_file` policy

Add `"output_file"` to `PATH_ARGUMENT_NAMES` in `tool_policy.py`. No MCP signature change. Add unit test `test_blocks_output_file_outside_allowed_roots`.

## F3 — Semgrep exit `1`

In `_run_semgrep`, after SARIF is on disk: treat return codes `0` and `1` as runner `pass`; let `_check_semgrep_sarif` apply `semgrep_block_levels`. Other codes remain `fail`.

## F4 — sync status on gate pass

In `_issue_status_from_verdict`, map `pass` → `in_progress` (not `done`). Update MCP/state tests that asserted `done`. `last_run_status=pass` still drives `plan_issue_flow` → Reporter.

## F5 — TruffleHog exit ≠ 0

In `_run_trufflehog`, if return code ≠ 0 **and** stdout is empty → runner `fail` (timeout/crash). Otherwise runner `pass` and defer to `_check_trufflehog_jsonl` / `block_trufflehog_unknown`.
