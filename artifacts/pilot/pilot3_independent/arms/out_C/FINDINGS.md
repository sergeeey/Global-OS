# Arm C FINDINGS — Paperclip workflow-controller @ 47c232b

**Verdict:** Not production-ready as-is. Six material defects confirmed with sealed local repro; one dual-path design claim rejected. Local minimal fixes verified (60 pytest); **Proposal ≠ Effect** — no external PR pushed.

| ID | Surface | Severity | Status |
|----|---------|----------|--------|
| C01 | event_log / issue_runner | High (correctness) | ASSERTED |
| C02 | tool_policy / MCP sync | High (security) | ASSERTED |
| C03 | tool_policy allowlist | High (security) | ASSERTED |
| C04 | tool_policy / MCP security | Medium (security) | ASSERTED |
| C05 | CLI security config | Medium (correctness) | ASSERTED |
| C06 | artifact_gate coverage | Medium (correctness / false-pass) | ASSERTED |
| C07 | issue_state vs issue_flow | — | REJECTED |

---

## C01 — Event log rejects authentic artifact-gate FAIL sequence

- **Path:** `workflow_controller/event_log.py` `_validate_consistency`; producer `issue_runner.py` `_final_verdict`
- **Trigger:** `run_issue_gates` on project whose artifacts fail tests → JSONL with `artifact_gate=fail` then `issue_gates` reason `artifact gate fail` → `verify_event_log`
- **Observed:** `verify_event_log` → `fail` / `artifact-gate final reason mismatch` (validator only accepted `"artifact gate blocked"` and required `status==blocked`)
- **Expected:** Faithfully emitted fail sequence validates (`pass`)
- **Severity:** High — breaks audit of legitimate fail paths; smoke only covered pass + blocked
- **Repro:** `REPRO/repro_C01_eventlog_artifact_fail.py` + `REPRO/evidence/pre_fix_repro_stdout.txt`

## C02 — `output_file` omitted from MCP path policy

- **Path:** `workflow_controller/tool_policy.py` `PATH_ARGUMENT_NAMES`; consumer `mcp_tools.py` `sync_issue_state`
- **Trigger:** `workflow_sync_issue_state` with `issue_file`/`event_log` inside allowed roots but `output_file` outside
- **Observed:** Policy `allow`; issue JSON written outside roots
- **Expected:** Policy `block`; no write
- **Severity:** High — path sandbox bypass on write surface
- **Repro:** `REPRO/repro_C02_output_file_path_bypass.py`
- **Note:** ToolCallSuccess (policy allow + write) ≠ intended WorldSuccess (containment)

## C03 — Empty `allowed_tools` disables allowlist

- **Path:** `tool_policy.py` `evaluate_tool_request` (`if policy.allowed_tools and ...`)
- **Trigger:** `ToolPolicy(allowed_tools=())` + unknown tool name
- **Observed:** `action=allow`
- **Expected:** Deny-all when allowlist empty (secure default)
- **Severity:** High — silent widen of tool surface
- **Repro:** `REPRO/repro_C03_empty_allowlist_bypass.py`

## C04 — Filesystem `semgrep_config` not path-checked

- **Path:** `tool_policy.py` path argument set; MCP passes `semgrep_config` into policy args
- **Trigger:** Absolute/outside-root `.yml` config with `run_semgrep=True`
- **Observed:** Policy `allow`; outside path never in `checked_paths`
- **Expected:** Filesystem config paths constrained like other path args; registry ids (`auto`) remain unconstrained
- **Severity:** Medium — policy-surface escape (WorldSuccess of scanner I/O not claimed without semgrep binary)
- **Repro:** `REPRO/repro_C04_semgrep_config_path_unchecked.py`

## C05 — CLI `--semgrep-block-level` cannot override defaults

- **Path:** `cli.py` argparse `action=append` + `default=["error","warning"]`
- **Trigger:** `verify-security … --semgrep-block-level error`
- **Observed:** `["error", "warning", "error"]`
- **Expected:** User-supplied levels replace defaults → `["error"]`
- **Severity:** Medium — operators cannot configure intended block set
- **Repro:** `REPRO/repro_C05_cli_block_level_append_default.py`

## C06 — Percent-shaped `line-rate` false-passes coverage gate

- **Path:** `artifact_gate.py` `_check_coverage`
- **Trigger:** `coverage.xml` with `line-rate="80"` (percent-shaped, not Cobertura ratio)
- **Observed:** Gate computes 8000% → `pass`
- **Expected:** Fail when `line-rate` ∉ `[0,1]`
- **Severity:** Medium — false WorldSuccess on malformed coverage artifact
- **Repro:** `REPRO/repro_C06_coverage_percent_as_rate.py`

## C07 — sync `pass→done` vs flow `pass→reporter` (REJECTED)

- **Path:** `issue_state._issue_status_from_verdict` vs `issue_flow._next_stage`
- **Observation:** Both behaviors are unit-tested as designed (`test_sync_issue_state_marks_done_on_pass`, `test_plan_moves_to_reporter_after_pass`)
- **Status:** REJECTED as material defect (dual-path intentional; not silent breakage)
- **Repro (negative):** `REPRO/negative_C07_sync_done_vs_reporter.py`

---

## Production readiness (epistemic)

```text
Smoke 54-pass  ≠  production readiness
Model confidence ≠ verification
Local fix verify ≠ merged upstream effect
```

Controller is suitable as a gated library only after C01–C06 land upstream (or equivalent). Authority/Temporal not live-wired this arm (per PROTOCOL_C).
