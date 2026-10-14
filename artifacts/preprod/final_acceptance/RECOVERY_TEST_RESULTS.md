# RECOVERY_TEST_RESULTS

## Real OS process kill

**Script:** `scripts/preprod_real_kill_recovery.py`  
**Artifact:** `recovery/REAL_KILL_RECOVERY.json`

Procedure:

1. Child process starts audit Goal; checkpoints after `brief_select`.  
2. Parent sends **SIGKILL** to the child PID (`returncode: -9`).  
3. Fresh process calls `resume_mission`.  
4. Delivery **SUCCEEDED**; `tool_calls.repo.audit == 1` (no silent replay).

This is a real process kill, not only an in-process `WorkflowAborted` unit simulation.  
It is **not** evidence of multi-hour durability.

## Automated e2e controls

- `kill_after_step="gateway_observe"` + resume (idempotent tool count)  
- pause / cancel operator controls  
- zero budget / deny capability / corrupt artifact negatives  
