# Persistent Research Long-Horizon Program

**LH-v1 (immutable):** 42h scheduled harness PASS — see `wall_48h/LH_V1_AUDIT.json`  
**LH-v2.1 (current):** T+48 barrier + `wall_seconds >= 172800` + **real OS process kill**  
**M1.5:** NOT claimed

## Honest status

```text
LH-v1 42h scheduled harness           ✅ PASS (immutable)
LH-v2 protocol (duration + criteria)  ✅
LH-v2.1 real OS kill + cold resume    ✅ (compressed preflight)
Literal 48h wall re-run               ❌ not started
M1.5                                  ❌ NOT CLAIMED
```

## Operator — Windows preflight then true 48h

```powershell
cd C:\dev\Global-OS
git pull
git rev-parse HEAD

# smoke OS kill
python -m global_os.evals.survival.os_process_kill controller --goal-id goal_smoke --work-dir artifacts\hardening\long_horizon_48h\os_kill_smoke

# ~90 min wall preflight (same contour as 48h, compressed hours)
$env:GOS_PREFLIGHT_HOUR_SECONDS = "112.5"
python -c @"
from pathlib import Path
from global_os.evals.survival.research_program import run_persistent_research_program
r = run_persistent_research_program(
    mode='preflight',
    artifact_root=Path('artifacts/hardening/long_horizon_48h/preflight_wall_windows_v2'),
    sleep=True,
)
print('passed', r.passed, 'fidelity', r.fidelity)
print('os_kill', r.provenance.get('os_kill'))
print('pids', r.provenance.get('initial_pid_os_kill'), '->', r.provenance.get('restart_pid'))
"@

# ONLY after preflight PASS — full 48h (will sleep to T+48)
$env:GOS_REQUIRE_48H = "1"
$env:GOS_START_RESEARCH_48H = "1"
python -c @"
from pathlib import Path
from global_os.evals.survival.research_program import run_persistent_research_program
r = run_persistent_research_program(
    mode='wall_48h',
    artifact_root=Path('artifacts/hardening/long_horizon_48h/wall_48h_v2'),
)
print(r.passed, r.fidelity, r.wall_seconds, r.required_wall_seconds)
"@
```

Do not rewrite `wall_48h/program_report.json` (LH-v1 historical evidence).
