# Freeze candidate — LH-COGNITIVE-v1

**Label:** FREEZE-LH-COGNITIVE-candidate  
**SHA full:** `7ab345e5badb00a8c97ffdb7010ee4eb42dac4bb`  
**SHA short:** `7ab345e`  
**Base decision:** Variant B (`M15_CLAIM_FORK.md`)  
**Not:** `5d15600` (durability/sum harness)

## Includes

- `cognitive_probes.py` / `cognitive_research_program.py`
- Contract: `LH_COGNITIVE_V1_CONTRACT.md`
- Tests: `tests/test_cognitive_research_program.py` (green on commit)

## Exam sequence (after this pin accepted)

```text
detached THIS_SHA
→ Windows os_kill smoke
→ cognitive_preflight (~96m, GOS_PREFLIGHT_HOUR_SECONDS=120)
→ cognitive_wall_48h (wall_seconds ≥ 172800)
→ freeze raw artifacts
→ independent audit
→ M1.5 decision (protocol scope)
```

## Still true

- m15_claimed false during run
- no patch-and-continue on exam SHA
- env repair OK; code defect → new freeze
