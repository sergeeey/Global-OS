# RC_ACCEPTANCE_FIXES — response to independent review

**Base evidence tip:** `d7977f8` (preserved)  
**This stage:** goal-specific postconditions + crash-window + usage split + unfamiliar Goal

## P0 — false-positive SUCCESS

| Item | Action |
|------|--------|
| Historical live SE | `POST_HOC_AUDIT_SE_LIVE_d7977f8.md` — acceptance **REJECTED**; archive not rewritten |
| Code | `goal_postconditions.py`: bind write criteria only when path token matches Goal + disk content matches report |
| Regression | `test_wrong_write_filename_does_not_succeed_goal` — `fix_marker.txt` ⇒ not SUCCEEDED |

## P1 — crash window after external effect

| Item | Evidence |
|------|----------|
| Script | `scripts/preprod_crash_window_recovery.py` |
| Artifact | `recovery/CRASH_WINDOW_RECOVERY.json` |
| Result | SIGKILL after write, before checkpoint; resume SUCCEEDED; write_calls=1; mtime unchanged |

## P1 — unfamiliar Goal

| Item | Evidence |
|------|----------|
| Goal | `examples/goal_accept_nonce.json` (`ACCEPT_NONCE_RC1.txt`) |
| Oracle | `independent_accept_write_goal` filesystem check |
| Test | `test_unfamiliar_accept_nonce_goal_independent_oracle` |

## P1 — resource accounting

Delivery now separates:

- `model_input_tokens` / `model_output_tokens` / `model_latency_ms` (measured from provider)
- `model_cost_usd` + `model_cost_forced` (Groq still forced `$0` tariff — not claimed as independent spend metering)

## Human gate

`v0.1.0-pre` remains **not self-accepted**. Re-review requested after these fixes.
