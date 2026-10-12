# Pack FIXES — minimal regression-safe patches (Proposal only)

**SHA base:** `47c232b`  
**Local verify:** `/tmp/pilot/p3-arm-C` → `60 passed`  
**External effect:** NOT applied (no Paperclip PR / merge)

## Patch artifact

`REPRO/patches/pilot3_arm_c_fixes.diff` + `REPRO/test_pilot3_arm_c_regressions.py`

## Per-finding fix

| ID | Change | Regression test |
|----|--------|-----------------|
| C01 | `event_log._validate_consistency`: accept `artifact gate {status}` for both fail and blocked; mirror security-gate blocked_reason rules | `test_c01_event_log_accepts_artifact_gate_fail` |
| C02 | Add `output_file` to `PATH_ARGUMENT_NAMES` | `test_c02_output_file_outside_roots_blocked` |
| C03 | Drop falsy short-circuit: `if tool_name not in policy.allowed_tools` (empty = deny-all) | `test_c03_empty_allowlist_denies_unknown_tool` |
| C04 | Conditional path check for filesystem-like `semgrep_config`; leave `auto`/registry ids alone | `test_c04_filesystem_semgrep_config_checked` |
| C05 | `--semgrep-block-level` `default=None`; apply `or ["error","warning"]` after parse | `test_c05_cli_block_level_overrides_default` |
| C06 | Reject `line-rate` outside `[0,1]` before scaling to percent | `test_c06_percent_shaped_line_rate_fails` |

## Test plan (sealed)

```bash
# On unmodified 47c232b: repro_C01..C06 exit 0 (CONFIRMED)
# Apply REPRO/patches/pilot3_arm_c_fixes.diff + copy regression test into tests/
cd tools/workflow-controller
python3 -m pytest -q tests/test_pilot3_arm_c_regressions.py   # 6 passed
python3 -m pytest -q                                         # 60 passed
```

## Semantic note (C03)

Empty `allowed_tools=()` previously meant “no allowlist restriction.” Patch changes this to deny-all. Default `DEFAULT_ALLOWED_TOOLS` unchanged; only explicit empty tuple callers are affected (secure-by-default).
