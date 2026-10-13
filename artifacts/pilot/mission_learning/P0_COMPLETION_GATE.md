# P0 — Goal Completion Gate

Executable terminal check: required world state + bound evidence + constraints.

| Status | Value |
|--------|-------|
| Trust zone | Verification plane (no LLM oracle) |
| Result enum | `ACHIEVED` / `PARTIAL` / `FAILED` / `UNKNOWN` |
| Code | `src/global_os/verification/completion_gate.py` |
| Tests | `tests/test_completion_gate.py` |

## Rules

- Plans finished ≠ goal achieved.
- `tool_response.success` alone never yields `ACHIEVED` (GOS-I13).
- LLM completion claims are ignored for the decision.
- Authority expansion or invariant break → `FAILED`.
- Does not replace Verification Fabric / EffectReceipt — binds them.

## Non-claims

- Not Continual SI measured.
- Not Challenge-GA execution.
- Not PRODUCTION_PROVEN.
