# Frozen validation exam — SHA `bfa58a0`

**Exam SHA (immutable for this attempt):** `bfa58a0236da1cbfdfa6125017f1ea7dfcb84fee`  
**Protocol:** LH-v2.1  
**Not claimed:** M1.5 / H-ORG / Continual SI / PRODUCTION_PROVEN  
**Y18-4-FC-IV:** leave as `BLOCKED_ENVIRONMENT` — do not invent PASS or treat as system failure

## Hard rules

1. Checkout **exactly** `bfa58a0`. Do **not** `git pull` / do **not** move to newer `main` before or during smoke/preflight/48h.
2. If Windows smoke or preflight finds a defect → **stop**. Fix on a branch → **new SHA** → new freeze candidate. Do not “patch the freeze”.
3. Do **not** start literal 48h until Windows wall preflight PASS on this SHA.
4. Do **not** set provider keys to force Y18-4 IV during this exam.

## Sequence

```text
bfa58a0
  → Windows os_kill smoke (seconds)
  → Windows 60–120m wall preflight
  → PASS only
  → literal 48h (separate gate)
  → artifact audit
  → M1.5 candidate conversation
```

## 0) Checkout freeze SHA (Windows)

```powershell
cd C:\dev\Global-OS
git fetch origin
git checkout --detach bfa58a0236da1cbfdfa6125017f1ea7dfcb84fee
git rev-parse HEAD
# must print: bfa58a0236da1cbfdfa6125017f1ea7dfcb84fee
$env:PYTHONPATH = "$PWD\src"
```

## 1) Windows os_kill smoke (seconds) — REQUIRED before 60–120m

```powershell
python -m global_os.evals.survival.os_process_kill controller `
  --goal-id goal_smoke_win `
  --work-dir artifacts\hardening\long_horizon_48h\os_kill_smoke_windows

# Expect JSON with passed=true, initial_pid ≠ restart_pid, child gone
# Save stdout to:
#   artifacts\hardening\long_horizon_48h\os_kill_smoke_windows\os_kill_result.json
```

**FAIL ⇒ stop. New freeze after fix.**  
Linux smoke PASS does **not** substitute this step.

## 2) Windows wall preflight 60–120 min

Uses `mode=preflight` with real sleeps (`PREFLIGHT_WALL`).  
Does **not** set `GOS_START_RESEARCH_48H` (that gate is for literal 48h only).

```powershell
# ~96 minutes: 48 schedule-hours × 120s
$env:GOS_PREFLIGHT_HOUR_SECONDS = "120"
$env:PYTHONPATH = "$PWD\src"

python -c @"
from pathlib import Path
from global_os.evals.survival.research_program import run_persistent_research_program
root = Path('artifacts/hardening/long_horizon_48h/windows_wall_preflight')
r = run_persistent_research_program(mode='preflight', artifact_root=root, sleep=True)
print('passed', r.passed, 'fidelity', r.fidelity, 'wall_s', round(r.wall_seconds,1), 'm15', r.m15_claimed, 'sha', r.provenance.get('git_sha'))
raise SystemExit(0 if r.passed else 1)
"@
```

**PASS requires:** `passed=true`, `fidelity=PREFLIGHT_WALL`, `m15_claimed=false`, provenance `git_sha` starts with `bfa58a0`.  
**FAIL ⇒ stop. New freeze after fix.**

## 3) Literal 48h — ONLY after step 2 PASS

Separate command; do not run yet unless preflight PASS is recorded:

```powershell
# Confirm still on freeze SHA
git rev-parse HEAD
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
Anything less is not a 48h PASS.

## Artifact handoff

After each step, copy reports into the repo working tree (or paste JSON) for audit:

- smoke: `os_kill_smoke_windows/os_kill_result.json`
- preflight: `windows_wall_preflight/program_report.json` + `PASS_CRITERIA.json`
- 48h: `wall_48h_lh_v2_1/program_report.json` + `PASS_CRITERIA.json`
