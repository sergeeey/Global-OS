# M1.5 EXAM — operator kickoff (Windows)

**Mode:** formal long-horizon exam  
**Not:** R4 · hardening · `main` development  
**Exam SHA (full):** `5d15600256a7afc7839f190ed3d889b33bc3217b`  
**Exam SHA (short):** `5d15600`  
**Protocol:** LH-v2.1  
**m15_claimed during run:** always `false` until post-run independent audit

## Absolute rules

1. Exam checkout stays on **exactly** `5d15600…`. No cherry-pick, no dep bump, no “tiny fix”.
2. Environmental issues (PATH, Python, disk) may be fixed **without code changes** and retry on same SHA.
3. Code/runtime defect ⇒ **stop exam validity** → record defect → fix on dev → regression → **new freeze SHA**.
4. No intellectual coaching of the system mid-run. Only pre-allowed physical/infra actions; **every** intervention → journal.
5. Finish gate for literal 48h: **`wall_seconds >= 172800` hard**. T+42 early stop is **not** a PASS.
6. After run: **freeze raw artifacts first**, then independent audit. Audit alone decides M1.5.

---

## Step 0 — clean exam environment

```powershell
cd C:\dev\Global-OS   # your clone
git fetch origin
git checkout --detach 5d15600256a7afc7839f190ed3d889b33bc3217b
git status
git rev-parse HEAD
```

**Expect:** clean tree (or only allowed untracked exam dirs) and HEAD = `5d15600256a7afc7839f190ed3d889b33bc3217b`.

If leftover `wall_48h` / untracked files block checkout → **move to backup**, do not delete LH-v1 evidence.

Set:

```powershell
$env:PYTHONPATH = "$PWD\src"
```

---

## Step 1 — Windows os_kill smoke (NOW)

```powershell
python -m global_os.evals.survival.os_process_kill controller `
  --goal-id goal_smoke_win_m15 `
  --work-dir artifacts\hardening\long_horizon_48h\os_kill_smoke_windows

# Save/confirm:
#   artifacts\hardening\long_horizon_48h\os_kill_smoke_windows\os_kill_result.json
# Expect: passed=true, child gone, cold resume semantics
```

| Outcome | Action |
|---------|--------|
| PASS | Go to Step 2 immediately — do not reopen architecture discussion |
| FAIL env-only | Fix environment; retry smoke on **same** SHA |
| FAIL code/runtime | Exam stopped; defect log; new freeze later |

---

## Step 2 — Windows 60–120m preflight

**Before launch**, write `artifacts/hardening/long_horizon_48h/windows_wall_preflight/EXAM_START.json`:

```json
{
  "exam_sha": "5d15600256a7afc7839f190ed3d889b33bc3217b",
  "host_os": "Windows",
  "host_name": "<fill>",
  "start_time_utc": "<fill ISO-8601>",
  "preflight_target_duration_min": 96,
  "workload_identity": "LH-v2.1 persistent research program mode=preflight",
  "fault_schedule": "program built-in schedule + os_kill where required",
  "operator_interventions": 0,
  "m15_claimed": false
}
```

Then run (~96 min example: 48 × 120s):

```powershell
$env:GOS_PREFLIGHT_HOUR_SECONDS = "120"
$env:PYTHONPATH = "$PWD\src"

python -c @"
from pathlib import Path
from global_os.evals.survival.research_program import run_persistent_research_program
root = Path('artifacts/hardening/long_horizon_48h/windows_wall_preflight')
r = run_persistent_research_program(mode='preflight', artifact_root=root, sleep=True)
sha = str((r.provenance or {}).get('git_sha', ''))
print('passed', r.passed, 'fidelity', r.fidelity, 'wall_s', round(r.wall_seconds,1), 'm15', r.m15_claimed, 'sha', sha)
ok = (
  r.passed
  and r.fidelity == 'PREFLIGHT_WALL'
  and r.m15_claimed is False
  and sha.startswith('5d15600')
)
raise SystemExit(0 if ok else 1)
"@
```

**PASS ⇒ Step 3 with no extra pause.**  
**FAIL ⇒ stop; do not patch `5d15600`.**

---

## Step 3 — literal ≥48h (only after preflight PASS)

```text
wall-clock >= 172800 seconds
+ real workload
+ scheduled faults
+ cold recovery where required
+ final terminal result
```

```powershell
git rev-parse HEAD   # still 5d15600…
$env:PYTHONPATH = "$PWD\src"
$env:GOS_REQUIRE_48H = "1"
$env:GOS_START_RESEARCH_48H = "1"
# FORBIDDEN: GOS_SOAK_ALLOW_FAST_WALL
# FORBIDDEN: GOS_SOAK_HOUR_SECONDS < 3600

python -c @"
from pathlib import Path
from global_os.evals.survival.research_program import run_persistent_research_program
root = Path('artifacts/hardening/long_horizon_48h/wall_48h_lh_v2_1')
r = run_persistent_research_program(mode='wall_48h', artifact_root=root, sleep=True)
print('passed', r.passed, 'fidelity', r.fidelity, 'wall_s', r.wall_seconds, 'm15', r.m15_claimed)
ok = r.passed and r.fidelity == 'WALL_CLOCK_48H' and float(r.wall_seconds) >= 172800 and r.m15_claimed is False
raise SystemExit(0 if ok else 1)
"@
```

During 48h: **zero code changes** to exam tree. Journal every infra intervention.

---

## Step 4 — freeze raw artifacts → independent audit

1. Freeze/copy raw reports (do not edit):
   - `os_kill_smoke_windows/os_kill_result.json`
   - `windows_wall_preflight/program_report.json` (+ PASS_CRITERIA)
   - `wall_48h_lh_v2_1/program_report.json` (+ PASS_CRITERIA)
   - intervention journal
2. Independent audit (separate contour) against locked gates **within protocol scope**.
3. Only then (narrow claim template — `docs/SCIENTIFIC_HONESTY_MAP.md`):

```text
PASS all locked gates → M1.5 candidate / claim discussion (scope-limited)
anything materially missing → M1.5 NOT CLAIMED
```

Do **not** upgrade a PASS into distributed exactly-once, production security, or universal reliability.

---

## Immediate next keystrokes

```text
Windows → detached 5d15600 → git status/rev-parse → smoke
```

If smoke green → preflight. Do not return to architecture debate.
