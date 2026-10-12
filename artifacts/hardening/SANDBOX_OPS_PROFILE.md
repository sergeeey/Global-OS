# Sandbox ops profile (OpenHands-grade isolation notes)

**Status:** documentation only (ADR-0013 P0b)  
**CI default:** `network=none`, memory/cpu limits, destroy-after-task ([task_runner.py](../../src/global_os/world/sandbox/task_runner.py))

## Enterprise nested isolation

Nested Docker / stronger RuntimeClass isolation is an **operator deployment
profile**, not a required PR CI gate (nested-overlay hosts may skip).

Do **not** mount the host Docker socket into agent sandboxes.

## Confirmation

Risk assessment is deterministic (`kernel/policy/confirm.py`). LLM-provided
`security_risk` fields are ignored.
