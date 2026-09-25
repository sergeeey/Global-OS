# Operator — STOP before wall_48h on `5d15600`

**Decision:** Variant **B** (`M15_CLAIM_FORK.md`)

## If 96m durability preflight is running

```text
LET IT FINISH
→ keep artifacts as DURABILITY_ENV / Windows fault-recovery evidence
→ do NOT promote to cognitive-real M1.5
```

## Do not

```text
git … wall_48h on 5d15600 for “real research 48h” claim
```

`5d15600` missions are `sum(1..20)==210` class. That answers a **narrower** question.

## Do next (cloud/dev on main → new freeze)

```text
LH-COGNITIVE-v1 implemented on main
→ regression tests green
→ freeze NEW SHA
→ Windows smoke + cognitive preflight on NEW SHA
→ literal ≥48h cognitive_wall_48h
→ independent audit
```

Cognitive entrypoint:

```powershell
# ONLY after checkout of the NEW freeze SHA (not 5d15600)
$env:PYTHONPATH = "$PWD\src"
$env:GOS_PREFLIGHT_HOUR_SECONDS = "120"
python -c "from pathlib import Path; from global_os.evals.survival.cognitive_research_program import run_cognitive_research_program; r=run_cognitive_research_program(mode='cognitive_preflight', artifact_root=Path(r'artifacts/hardening/long_horizon_48h/windows_cognitive_preflight'), sleep=True); print(r.passed, r.fidelity, r.wall_seconds, r.m15_claimed, r.provenance.get('git_sha')); raise SystemExit(0 if r.passed else 1)"
```
