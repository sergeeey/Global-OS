# Persistent Research 48h Program

**Phase:** Empirical Hardening COMPLETE → Long-Horizon Validation ENTRY  
**Status:** PREPARED · compressed preflight PASS · wall proof NOT started · M1.5 NOT claimed  
**Code freeze:** no code changes unless Windows wall preflight finds a structural bug

## What this proves (when wall 48h runs)

```text
Goal survives time
State survives restart
Epistemic integrity survives contradiction/invalidation
Authority boundaries survive faults
No duplicate irreversible effects
Blocked resources degrade gracefully
Mission state remains auditable
Program resumes instead of starting over
```

Evaluate **only** frozen PASS criteria — not impressions.  
FAIL is a valuable failure case, not a project collapse.

## Scenario (frozen)

```text
T0 Goal Contract
→ research missions (LH-1..3 deterministic)
→ durable checkpoints
→ provider failure / swap (harness)
→ process kill + restart
→ contradictory evidence
→ source invalidation
→ cold epistemic restore
→ budget / constraint change
→ continue work
→ stop condition
→ Goal + Epistemic + Authority integrity audit
```

## Operator order (Windows)

### 1. Wall preflight 60–120 min (same contour as 48h)

**Retry after LH-FC-PORTABILITY-SLEEP** (Unix `sleep` → `sys.executable`).  
Pull latest main before running. Not an M1.5 proof.

```powershell
cd C:\dev\Global-OS
git pull
git rev-parse HEAD
# Confirm harness no longer uses bare "sleep":
Select-String -Path src\global_os\evals\survival\harness.py -Pattern 'execute\(\["sleep"'
# (should find nothing)

# Compress 48h schedule into ~90 minutes wall time:
# hour_seconds = 90*60/48 = 112.5
$env:GOS_PREFLIGHT_HOUR_SECONDS = "112.5"
python -c @"
from pathlib import Path
from global_os.evals.survival.research_program import run_persistent_research_program
r = run_persistent_research_program(
    mode='preflight',
    artifact_root=Path('artifacts/hardening/long_horizon_48h/preflight_wall_windows'),
    sleep=True,
)
print('passed', r.passed, 'fidelity', r.fidelity, 'wall_s', r.wall_seconds)
print('m15_claimed', r.m15_claimed)
"@
```

If structural failure → classify, minimal fix, stop.  
If PASS → **freeze that commit/config**; no cosmetics.

### 2. Full wall 48h (only after freeze)

```powershell
$env:GOS_REQUIRE_48H = "1"
$env:GOS_START_RESEARCH_48H = "1"
# real hours (default); do not set GOS_SOAK_ALLOW_FAST_WALL
python -c @"
from pathlib import Path
from global_os.evals.survival.research_program import run_persistent_research_program
r = run_persistent_research_program(
    mode='wall_48h',
    artifact_root=Path('artifacts/hardening/long_horizon_48h/wall_48h'),
)
print(r.as_dict())
"@
```

During the run: no manual help except actions allowed by contract.

### 3. After result

```text
48h PASS → review artifacts → confirm no hidden intervention → M1.5 candidate
48h FAIL → classify → minimal fix → regression → compressed replay → new attempt
```

## Compressed CI preflight (already done)

```bash
make preflight-48h
```

≠ wall proof.

## Out of scope

- H-ORG proof
- Continual self-improvement measurement
- Re-touching provider keys
- Claiming M1.5 from any preflight alone
