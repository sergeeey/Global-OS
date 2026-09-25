# Persistent Research Long-Horizon Program

**Phase:** Scientific dogfood (**Y19**) active. LH Windows 96m / literal 48h **deferred**.  
**LH-v1 (immutable):** 42h scheduled harness PASS — `wall_48h/LH_V1_AUDIT.json`  
**LH-v2.1:** protocol ready; not under formal exam right now  
**Y18:** failure-mode diversity MET  
**Stable point:** `bfa58a0` (intermediate — may be superseded if Y19 finds bugs)  
**M1.5:** NOT claimed

## Plan (locked)

```text
NOW
  Windows os_kill smoke on exact bfa58a0 (seconds) — still useful
  Y19-H1 scientific dogfood (unknown-answer research)
  failures → minimal fix → regression → possibly new SHA

DEFERRED
  Windows 96m wall preflight
  literal 48h / M1.5 exam

LATER
  new freeze SHA after science dogfood stabilizes
  → Windows preflight → literal 48h as integration exam
```

## Windows smoke only (seconds)

See `WINDOWS_FROZEN_EXAM.md` §0–§1. Skip §2 (96m) and §3 (48h) for now.

```powershell
# backup untracked wall_48h if checkout blocks, then:
git checkout --detach bfa58a0236da1cbfdfa6125017f1ea7dfcb84fee
$env:PYTHONPATH = "$PWD\src"
python -m global_os.evals.survival.os_process_kill controller `
  --goal-id goal_smoke_win `
  --work-dir artifacts\hardening\long_horizon_48h\os_kill_smoke_windows
```

## Y19

Full TZ: `artifacts/y19/Y19-H1-transient-early-warning/TZ.md`
