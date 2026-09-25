# Persistent Research Long-Horizon Program

**LH-v1 (immutable):** 42h scheduled harness PASS — see `wall_48h/LH_V1_AUDIT.json`  
**Phase:** Long-Horizon protocol repaired; **validation deferred** while real-world hardening continues.  
**LH-v1 (immutable):** 42h scheduled harness PASS — `wall_48h/LH_V1_AUDIT.json`  
**LH-v2.1:** T+48 + duration gate + real OS kill — compressed preflight PASS  
**M1.5 / literal 48h:** NOT now

## Plan (locked)

```text
NOW
  optional: Windows os_kill smoke (seconds)
  real dogfood 2–4 missions
  failure → minimal fix → regression
  no 90m preflight / no 48h while code moves

FREEZE when
  no open critical defects in state/recovery/authority/eval

THEN
  freeze SHA
  → Windows wall preflight 60–120min
  → literal 48h on real persistent research workload
  → audit → M1.5 candidate
```

## Optional smoke only (seconds)

```powershell
cd C:\dev\Global-OS
git pull
python -m global_os.evals.survival.os_process_kill controller `
  --goal-id goal_smoke `
  --work-dir artifacts\hardening\long_horizon_48h\os_kill_smoke
```

If PASS — stop Long-Horizon tooling work; return to dogfood.  
Do **not** start 90m preflight until freeze candidate.
