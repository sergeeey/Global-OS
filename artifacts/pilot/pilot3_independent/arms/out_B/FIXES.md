# Pilot 3 Arm B — Minimal fixes

Applied under `/tmp/pilot/p3-arm-B/tools/workflow-controller/` for fail→pass demo. Upstream Paperclip should port the same diffs.

## B-01 — Add `output_file` to path policy

**File:** `workflow_controller/tool_policy.py`  
**Change:** include `"output_file"` in `PATH_ARGUMENT_NAMES`.  
**Test:** `B01*` red→green.

## B-02 — Re-check nested issue paths in MCP sync

**File:** `workflow_controller/mcp_tools.py`  
**Change:** after loading issue, resolve `output_location` / execution scan paths and call `evaluate_tool_request` again before running gates.  
**Test:** `B02*` red→green.  
**Regression-safe:** existing MCP sync tests keep `Path.cwd()` in allowed roots (fixtures resolve under cwd).

## B-03 — Require `summary.failed`

**File:** `workflow_controller/artifact_gate.py`  
**Change:** stop defaulting missing `failed` to `0`; fail when missing/non-integer (mirror `passed`).  
**Test:** `B03*` red→green.

## B-04 — Accept artifact-gate fail event logs

**File:** `workflow_controller/event_log.py`  
**Change:** expected reason `artifact gate {status}` for single-prior sequences; only require `blocked_reason` when status is `blocked`.  
**Test:** `B04*` red→green; existing blocked/pass event-log tests remain green.

## B-05 — Empty allow-list denies

**File:** `workflow_controller/tool_policy.py`  
**Change:** `if tool_name not in policy.allowed_tools:` (remove truthiness short-circuit on empty tuple).  
**Test:** `B05*` red→green; default `DEFAULT_ALLOWED_TOOLS` unchanged so smoke stays green.

## Verification

```text
# before patch
pytest out_B/REPRO/test_confirmed_defects.py  → 7 failed

# after patch in /tmp/pilot/p3-arm-B
pytest out_B/REPRO/test_confirmed_defects.py  → 7 passed
pytest tools/workflow-controller/tests        → 54 passed
```
