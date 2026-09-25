# Freeze candidate — LH-COGNITIVE-v1

**Label:** FREEZE-LH-COGNITIVE-candidate  
**SHA full:** `92f8bbcd6bec6a0d6139e4ec507ff99366b925aa`  
**SHA short:** `92f8bbc`  
**Base decision:** Variant B (`M15_CLAIM_FORK.md`)  
**Supersedes for cognitive exam:** `5d15600` (keep as durability ENV evidence only)

## Includes

- `cognitive_probes.py` / `cognitive_research_program.py`
- Contract: `LH_COGNITIVE_V1_CONTRACT.md`
- Tests: `tests/test_cognitive_research_program.py`

## Exam sequence

```text
detached 92f8bbcd6bec6a0d6139e4ec507ff99366b925aa
→ Windows os_kill smoke
→ cognitive_preflight (~96m)
→ cognitive_wall_48h (wall_seconds ≥ 172800)
→ freeze raw artifacts → independent audit → M1.5 (scope-limited)
```
