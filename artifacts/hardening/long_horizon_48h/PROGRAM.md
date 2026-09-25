# Persistent Research Long-Horizon Program

**Phase:** **Frozen validation** of SHA `bfa58a0` — Windows smoke → Windows wall preflight → (only if PASS) literal 48h.  
**LH-v1 (immutable):** 42h scheduled harness PASS — `wall_48h/LH_V1_AUDIT.json`  
**LH-v2.1:** T+48 + duration gate + real OS kill — compressed preflight PASS  
**Y18:** 4 failure-mode classes all SUPPORTED — `artifacts/hardening/dogfood_fm/`  
**Freeze exam SHA:** `bfa58a0236da1cbfdfa6125017f1ea7dfcb84fee`  
**M1.5:** NOT claimed

## Plan (locked)

```text
FROZEN SHA = bfa58a0
  do not git pull / do not move main under the exam checkout

NOW (operator Windows)
  1) Windows os_kill smoke (seconds) — REQUIRED before 60–120m
  2) Windows wall preflight 60–120m (PREFLIGHT_WALL)
  FAIL ⇒ fix → new SHA → new freeze (do not patch this freeze)

THEN (only if preflight PASS)
  literal 48h on real persistent workload (exam of bfa58a0)
  → artifact audit → M1.5 candidate conversation
```

## Exact runbook

See **`WINDOWS_FROZEN_EXAM.md`** (checkout rules, PowerShell, PASS criteria).

## Rules

- Linux `os_kill` smoke PASS ≠ Windows portability proof
- `Y18-4-FC-IV` stays `BLOCKED_ENVIRONMENT` (honest; not PASS; not system failure)
- Do not set `GOS_START_RESEARCH_48H=1` until Windows wall preflight PASS
