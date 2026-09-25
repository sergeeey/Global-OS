# Persistent Research Long-Horizon Program

**LH-v1 (immutable):** 42h scheduled harness PASS — see `wall_48h/LH_V1_AUDIT.json`  
**LH-v2 (current protocol):** T+48 barrier + `wall_seconds >= 172800` for `WALL_CLOCK_48H`  
**M1.5:** NOT claimed

## Honest status

```text
Long-Horizon scheduled program (v1)   ✅ PASS (~42h)
Literal 48h survival                  ❌ NOT PROVEN (v1)
LH-v2 protocol                        ✅ patched in code
True 48h wall re-run                  ❌ not started
```

## What LH-v1 actually proved

High confidence: 42h wall scheduler, 9/9 harness injections executed, GIS under
original criteria, null preserved, authority not expanded, LH-3 continued.

Not proven: literal 48h, real OS process death, shared-state perturbations at
scheduled offsets (v1), full GOS-I12 downstream invalidation chain (v1 criterion
was a false positive).

## LH-v2 gates

```text
schedule_completed
AND missions_completed
AND terminal_barrier_t48
AND wall_seconds >= 172800   # for WALL_CLOCK_48H
AND hard_integrity_gates_pass
AND invalidated_evidence_propagates (non-empty downstream chain)
```

## Operator order

```powershell
cd C:\dev\Global-OS
git pull
# compressed first
python -c "from global_os.evals.survival.research_program import run_preflight; print(run_preflight().passed)"

# then Windows wall preflight ~90min
$env:GOS_PREFLIGHT_HOUR_SECONDS = "112.5"
python -c @"
from pathlib import Path
from global_os.evals.survival.research_program import run_persistent_research_program
r = run_persistent_research_program(mode='preflight', artifact_root=Path('artifacts/hardening/long_horizon_48h/preflight_wall_windows_v2'), sleep=True)
print(r.passed, r.fidelity, r.wall_seconds, r.provenance)
"@

# only after preflight PASS — full wall (will take full 48h)
$env:GOS_REQUIRE_48H = "1"
$env:GOS_START_RESEARCH_48H = "1"
python -c @"
from pathlib import Path
from global_os.evals.survival.research_program import run_persistent_research_program
r = run_persistent_research_program(mode='wall_48h', artifact_root=Path('artifacts/hardening/long_horizon_48h/wall_48h_v2'))
print(r.passed, r.fidelity, r.wall_seconds, r.required_wall_seconds)
"@
```

Do not rewrite `wall_48h/program_report.json` (LH-v1 historical evidence).
