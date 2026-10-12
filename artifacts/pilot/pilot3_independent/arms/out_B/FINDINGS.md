# Pilot 3 Arm B — Findings

**Target:** Paperclip-AI---2026 @ `47c232b` — `tools/workflow-controller/`  
**Readiness claim:** **Not production-ready** for MCP/policy-bound use (see NOTES). Defects below are separate evidence.

## CONFIRMED

### B-01 — `output_file` escapes tool policy roots (security)

| Field | Value |
|-------|-------|
| **Path** | `workflow_controller/tool_policy.py` (`PATH_ARGUMENT_NAMES`); `workflow_controller/mcp_tools.py` (`sync_issue_state`) |
| **Trigger** | MCP `workflow_sync_issue_state` with `issue_file`/`event_log` inside `allowed_roots` but `output_file` outside |
| **Observed** | Policy `action=allow`; issue JSON written outside roots |
| **Expected** | Policy `block` — all filesystem write paths constrained by `allowed_roots` |
| **Severity** | **High** (unauthorized write via MCP policy layer) |
| **Repro** | `REPRO/test_confirmed_defects.py::B01*` |

### B-02 — Nested issue paths bypass policy (security)

| Field | Value |
|-------|-------|
| **Path** | `workflow_controller/mcp_tools.py` (`sync_issue_state` → `run_issue_gates_from_issue`) |
| **Trigger** | Issue JSON under allowed root whose `output_location` / scan paths point outside roots |
| **Observed** | Policy allows; gates read/execute against out-of-root project and mark issue done |
| **Expected** | Second policy check on resolved nested paths; `block` if outside roots |
| **Severity** | **High** (path allowlist bypass / arbitrary project read under gate runner) |
| **Repro** | `REPRO/test_confirmed_defects.py::B02*` |

### B-03 — Missing `summary.failed` treated as zero (correctness)

| Field | Value |
|-------|-------|
| **Path** | `workflow_controller/artifact_gate.py` (`_check_test_results`) |
| **Trigger** | `test-results.json` with `summary.passed` only (no `failed`) |
| **Observed** | Artifact gate `pass` (`failed` defaulted to `0`) |
| **Expected** | Fail — README requires `summary.passed` **and** `summary.failed` |
| **Severity** | **Medium** (gate accepts incomplete attestation) |
| **Repro** | `REPRO/test_confirmed_defects.py::B03*` |

### B-04 — `verify_event_log` rejects legitimate artifact-gate **fail** logs (correctness / false-positive)

| Field | Value |
|-------|-------|
| **Path** | `workflow_controller/event_log.py` (`_validate_consistency`); producer `issue_runner.py` reason `artifact gate {status}` |
| **Trigger** | `run_issue_gates` fails artifact checks (e.g. failed tests) with `--event-log`, then `verify-event-log` |
| **Observed** | Runner emits `issue_gates` / `fail` / `artifact gate fail`; verifier returns `fail` / `artifact-gate final reason mismatch` |
| **Expected** | Verifier accepts both `artifact gate fail` and `artifact gate blocked` (matches runner) |
| **Severity** | **High** (false-positive breakage of legitimate fail workflow traffic) |
| **Repro** | `REPRO/test_confirmed_defects.py::B04*` |

### B-05 — Empty `allowed_tools` silently allows all tools (security)

| Field | Value |
|-------|-------|
| **Path** | `workflow_controller/tool_policy.py` (`evaluate_tool_request`) |
| **Trigger** | `ToolPolicy(allowed_tools=())` then request unknown tool e.g. `shell` |
| **Observed** | `action=allow` because `if policy.allowed_tools and ...` short-circuits |
| **Expected** | Empty allow-list means allow nothing (block unknown / all) |
| **Severity** | **Medium** (footgun; misconfiguration → open policy) |
| **Repro** | `REPRO/test_confirmed_defects.py::B05*` |

## REJECTED / NOT_REPRODUCED (retained)

| ID | Claim | Disposition | Notes |
|----|-------|-------------|-------|
| R-01 | Sync→`done` skips reporter/devops vs flow plan | **REJECTED (by design)** | Tests lock `sync_issue_state` → `done` on gate pass; flow plan for `in_progress`+`pass` → reporter is a separate mode |
| R-02 | Path prefix confusion (`/tmp/projects` vs `/tmp/projects-evil`) | **NOT_REPRODUCED** | `Path.relative_to` correctly blocks |
| R-03 | Only-semgrep (omit trufflehog) security pass | **REJECTED (API contract)** | Artifacts are individually optional; both-null blocks; omission is caller config |
| R-04 | Coverage XML XXE | **NOT_REPRODUCED / speculative** | No PoC; stdlib ElementTree does not expand external entities by default |
| R-05 | `run_semgrep` exit-code vs `block_levels` false positive | **NOT_REPRODUCED in budget** | Likely tension when live scanners run; no confirmable local PoC without installing scanners / network |

## Counts

| Category | Count |
|----------|-------|
| CONFIRMED | **5** |
| REJECTED / NOT_REPRODUCED | **5** |
| Unsupported speculative (no PoC, not counted as findings) | **0** additional beyond R-04/R-05 retention |

## Fix demo

- Red: `REPRO/red_before_fix.txt` — 7 failed  
- Green after minimal patches in `/tmp/pilot/p3-arm-B`: `REPRO/green_after_fix.txt` — 7 passed  
- Smoke after fix: `REPRO/smoke_after_fix.txt` — **54 passed**  
- Patch notes: `FIXES.md`
