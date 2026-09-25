# Persistent Research Long-Horizon Program

**Phase:** Freeze candidate **pinned** (`bfa58a0`). Windows preflight next; literal 48h is final exam of this SHA.  
**LH-v1 (immutable):** 42h scheduled harness PASS — `wall_48h/LH_V1_AUDIT.json`  
**LH-v2.1:** T+48 + duration gate + real OS kill — compressed preflight PASS  
**Y18:** 4 failure-mode classes all SUPPORTED — `artifacts/hardening/dogfood_fm/`  
**Freeze:** `bfa58a0` — see `dogfood_fm/FREEZE_READINESS.json`  
**M1.5 / literal 48h:** NOT until Windows preflight PASS

## Plan (locked)

```text
DONE
  Y18 dogfood: evidence / effect-recovery / authority / provider-degradation
  freeze candidate SHA pinned: bfa58a0

NOW
  optional: Windows os_kill smoke (seconds)
  Windows wall preflight 60–120min on bfa58a0
  no literal 48h before preflight PASS

THEN
  literal 48h on real persistent research workload (exam of frozen SHA)
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
