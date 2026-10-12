# Pilot 3 Arm A — workflow-controller findings

Checkout: `/tmp/pilot/p3-arm-A` @ `47c232b` (Paperclip-AI---2026)  
Focus: `tools/workflow-controller/`  
Smoke (54 passed) not counted as findings.  
Regressions: `REPRO/test_pilot3_arm_a_regressions.py` (5 failed pre-fix → 5 passed post-fix).

---

## 1. Event-log gate false-fails legitimate artifact-gate FAIL

- **Severity:** major  
- **Path:** `workflow_controller/event_log.py` (`_validate_consistency`), `workflow_controller/issue_runner.py` (final reason for artifact short-circuit)  
- **Trigger:** `run-issue-gates` / `run_issue_gates` where artifact checks fail (e.g. `summary.failed > 0`), with `--event-log` written, then `verify-event-log` on that log.  
- **Observed:** Pipeline correctly emits final status `fail` with reason `artifact gate fail`. `verify_event_log` returns `fail` with `artifact-gate final reason mismatch` because the validator only accepts reason/status `artifact gate blocked` for the single-prior-event path.  
- **Expected:** A consistent artifact-gate FAIL sequence must pass event-log validation (same as security-gate FAIL already does).  
- **Evidence:** `REPRO/pre_fix_results.txt` F1; confirmed via direct repro.

---

## 2. MCP `output_file` bypasses path policy (arbitrary write)

- **Severity:** critical  
- **Path:** `workflow_controller/tool_policy.py` (`PATH_ARGUMENT_NAMES`), `workflow_controller/mcp_tools.py` (`WorkflowToolService.sync_issue_state`)  
- **Trigger:** MCP/tool call `workflow_sync_issue_state` with `issue_file` inside an allowed root and `output_file` outside all allowed roots.  
- **Observed:** `evaluate_tool_request` returns `allow` because `output_file` is omitted from `PATH_ARGUMENT_NAMES`. Service writes the synced issue JSON to the denied path.  
- **Expected:** Path policy must block (and not write) `output_file` outside `allowed_roots`, matching other path arguments (`issue_file`, `event_log`, `output_dir`, …).  
- **Evidence:** Policy allow + file written under denied temp root; `REPRO` F2.

---

## 3. Semgrep runner exit code false-fails non-blocking findings

- **Severity:** major  
- **Path:** `workflow_controller/security_gate.py` (`_run_semgrep`)  
- **Trigger:** `verify_security_scans(..., run_semgrep=True)` when Semgrep exits `1` (findings present) but SARIF results are only `note` (not in `semgrep_block_levels`, default `error`/`warning`).  
- **Observed:** `semgrep.run` marked `fail` → overall security gate `fail`, while `semgrep.sarif` check correctly `pass`.  
- **Expected:** Finding severity policy is owned by SARIF parsing / `semgrep_block_levels`. Exit `1` with produced SARIF must not override a non-blocking SARIF verdict. Exit codes other than `0`/`1` remain runner failures.  
- **Evidence:** Mocked Semgrep exit `1` + note-only SARIF; `REPRO` F3.

---

## 4. `sync_issue_state` marks gate pass as `done`, skipping Reporter/DevOps

- **Severity:** major  
- **Path:** `workflow_controller/issue_state.py` (`_issue_status_from_verdict`), interacts with `workflow_controller/issue_flow.py`  
- **Trigger:** Successful `run_issue_gates` / MCP `workflow_sync_issue_state` on a clean project, then `plan_issue_flow` on the synced issue.  
- **Observed:** Sync sets `status=done`. Plan then reports `next_stage=None` and marks ceo/builder/scanner/**reporter**/**devops** all `complete` without Reporter or DevOps acting.  
- **Expected:** Artifact+security gate pass means Builder/Scanner verification succeeded; flow should advance to Reporter (`in_progress` + `last_run_status=pass`), not terminal `done`.  
- **Evidence:** Sync→`done` vs plan-with-`in_progress`+pass→`reporter`; `REPRO` F4. Existing unit tests previously encoded the buggy `done` behavior.

---

## 5. TruffleHog runner exit code ignores `block_trufflehog_unknown=False`

- **Severity:** major  
- **Path:** `workflow_controller/security_gate.py` (`_run_trufflehog`)  
- **Trigger:** `run_trufflehog=True` with process exit ≠ 0 and JSONL containing only `Verified: false` findings while `block_trufflehog_unknown=False`.  
- **Observed:** `trufflehog.run` `fail` → overall gate `fail`, while `trufflehog.jsonl` correctly `pass` under the configured policy.  
- **Expected:** JSONL checker (and `block_trufflehog_unknown`) decide finding disposition. Non-zero exit with usable stdout must not false-fail; empty-output non-zero (crash/timeout) should still fail the runner.  
- **Evidence:** Mocked exit `183` + unverified finding; `REPRO` F5.

---

## Counts

| Severity | Count |
|----------|-------|
| critical | 1 |
| major    | 4 |
| minor    | 0 |
| hygiene  | 0 |
| **total**| **5** |
