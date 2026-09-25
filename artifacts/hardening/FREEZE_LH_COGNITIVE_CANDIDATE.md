# Freeze candidate — LH-COGNITIVE-v1

**Label:** FREEZE-LH-COGNITIVE-candidate  
**Exam SHA full:** `7ab345e5badb00a8c97ffdb7010ee4eb42dac4bb`  
**Exam SHA short:** `7ab345e`  
**Pin docs may be newer than exam SHA** (honesty/runbook only).  
**Base decision:** Variant B (`M15_CLAIM_FORK.md`)  
**Supersedes for cognitive exam:** `5d15600`

## Exam sequence

```text
detached 7ab345e5badb00a8c97ffdb7010ee4eb42dac4bb
→ Windows os_kill smoke  
→ cognitive_preflight (~96m, GOS_PREFLIGHT_HOUR_SECONDS=120)
→ cognitive_wall_48h (wall_seconds ≥ 172800)
→ freeze raw artifacts → independent audit → M1.5 (protocol scope)
```

Code under exam SHA includes cognitive harness. Later doc-only commits on main do not change exam tree.
