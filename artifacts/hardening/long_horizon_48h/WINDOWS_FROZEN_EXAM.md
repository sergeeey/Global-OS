# Frozen validation exam — SHA `5d15600` (FREEZE-R1R3-v1)

**Exam SHA (full):** `5d15600256a7afc7839f190ed3d889b33bc3217b`  
**Label:** `FREEZE-R1R3-v1` — see `../FREEZE_R1_R3.md`  
**Protocol:** LH-v2.1  
**Status:** ready for **formal Windows long-horizon validation**  
**Not claimed:** M1.5 / H-ORG / Continual SI / PRODUCTION_PROVEN / universal GOS advantage

> Prior intermediate pin `bfa58a0` is **superseded** for new exams. Do not use it.

## Freeze meaning (not a project pause)

```text
Freeze = do not change the version under exam.
Freeze ≠ stop the whole project.
```

- On exam checkout `5d15600`: **no mid-run fixes**, no `git pull`, no feature work.
- If Windows preflight finds a bug: record failure → fix on a **branch/main** → **new freeze SHA** → re-exam.  
  **Do not patch `5d15600` in place and pretend it still passes.**
- R4/R5 on `main` is allowed only if you accept that `5d15600` is no longer the final candidate.

## Hard rules

1. Checkout **exactly** `5d15600…`. Verify with `git rev-parse HEAD`.
2. If untracked `wall_48h/*.json` block checkout → **move to backup**, do not delete LH-v1 evidence.
3. Smoke FAIL or preflight FAIL ⇒ stop; new freeze after fix.
4. Literal 48h **only** after Windows wall preflight PASS on this SHA.
5. Compressed Linux preflight / Linux os_kill **do not** substitute Windows steps.

## Sequence

```text
checkout --detach 5d15600256a7afc7839f190ed3d889b33bc3217b
  → §1 Windows os_kill smoke (seconds)
  → §2 Windows 60–120m wall preflight
  → PASS only
  → §3 literal ≥48h on real workload (no mid-run fixes)
  → independent audit
  → M1.5 candidate conversation
```

## 0) Checkout freeze SHA (Windows)

```powershell
cd C:\dev\Global-OS   # or your clone path
git fetch origin
git checkout --detach 5d15600256a7afc7839f190ed3d889b33bc3217b
git rev-parse HEAD
# must print: 5d15600256a7afc7839f190ed3d889b33bc3217b
$env:PYTHONPATH = "$PWD\src"
```

## 1) Windows os_kill smoke (seconds) — REQUIRED before 60–120m

```powershell
python -m global_os.evals.survival.os_process_kill controller `
  --goal-id goal_smoke_win `
  --work-dir artifacts\hardening\long_horizon_48h\os_kill_smoke_windows

# Expect JSON with passed=true, initial_pid ≠ restart_pid, child gone
# Save stdout / result to:
#   artifacts\hardening\long_horizon_48h\os_kill_smoke_windows\os_kill_result.json
```

**FAIL ⇒ stop. New freeze after fix.**

## 2) Windows wall preflight 60–120 min

Uses `mode=preflight` with real sleeps (`PREFLIGHT_WALL`).  
Does **not** set `GOS_START_RESEARCH_48H`.

```powershell
# ~96 minutes: 48 schedule-hours × 120s
$env:GOS_PREFLIGHT_HOUR_SECONDS = "120"
$env:PYTHONPATH = "$PWD\src"

python -c @"
from pathlib import Path
from global_os.evals.survival.research_program import run_persistent_research_program
root = Path('artifacts/hardening/long_horizon_48h/windows_wall_preflight')
r = run_persistent_research_program(mode='preflight', artifact_root=root, sleep=True)
sha = (r.provenance or {}).get('git_sha', '')
print('passed', r.passed, 'fidelity', r.fidelity, 'wall_s', round(r.wall_seconds,1), 'm15', r.m15_claimed, 'sha', sha)
ok = r.passed and r.fidelity == 'PREFLIGHT_WALL' and r.m15_claimed is False and str(sha).startswith('5d15600')
raise SystemExit(0 if ok else 1)
"@
```

**PASS requires:** `passed=true`, `fidelity=PREFLIGHT_WALL`, `m15_claimed=false`, provenance `git_sha` starts with `5d15600`.  
**FAIL ⇒ stop. New freeze after fix (do not patch 5d15600).**

## 3) Literal 48h — ONLY after step 2 PASS

Real persistent research workload. No mid-run fixes. No fast-wall cheats.

```powershell
git rev-parse HEAD   # still 5d15600…
$env:PYTHONPATH = "$PWD\src"
$env:GOS_REQUIRE_48H = "1"
$env:GOS_START_RESEARCH_48H = "1"
# Do NOT set GOS_SOAK_ALLOW_FAST_WALL
# Do NOT set GOS_SOAK_HOUR_SECONDS below 3600

python -c @"
from pathlib import Path
from global_os.evals.survival.research_program import run_persistent_research_program
root = Path('artifacts/hardening/long_horizon_48h/wall_48h_lh_v2_1')
r = run_persistent_research_program(mode='wall_48h', artifact_root=root, sleep=True)
print('passed', r.passed, 'fidelity', r.fidelity, 'wall_s', r.wall_seconds, 'm15', r.m15_claimed)
raise SystemExit(0 if r.passed else 1)
"@
```

Literal PASS requires `fidelity=WALL_CLOCK_48H` and `wall_seconds >= 172800`.  
Anything less is not a 48h PASS. **Still ≠ automatic M1.5** — needs independent audit.

## Artifact handoff

- smoke: `os_kill_smoke_windows/os_kill_result.json`
- preflight: `windows_wall_preflight/program_report.json` + `PASS_CRITERIA.json`
- 48h: `wall_48h_lh_v2_1/program_report.json` + `PASS_CRITERIA.json`
