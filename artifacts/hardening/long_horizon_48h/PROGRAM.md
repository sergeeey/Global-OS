# Persistent Research Long-Horizon Program

**Phase:** Y18 failure-mode dogfood complete; **pin freeze candidate** next. LH validation deferred.  
**LH-v1 (immutable):** 42h scheduled harness PASS — `wall_48h/LH_V1_AUDIT.json`  
**LH-v2.1:** T+48 + duration gate + real OS kill — compressed preflight PASS  
**Y18:** 4 failure-mode classes all SUPPORTED — `artifacts/hardening/dogfood_fm/`  
**M1.5 / literal 48h:** NOT now

## Plan (locked)

```text
DONE
  Y18 dogfood: evidence / effect-recovery / authority / provider-degradation
  no open critical defects in freeze scope (see FREEZE_READINESS.json)

NOW
  pin freeze candidate SHA
  optional: Windows os_kill smoke (seconds)
  no 90m preflight / no 48h until freeze pinned

THEN
  Windows wall preflight 60–120min on frozen SHA
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

If PASS — optional confirmation only; does not replace freeze pin.  
Do **not** start 90m preflight until freeze candidate SHA is pinned.
