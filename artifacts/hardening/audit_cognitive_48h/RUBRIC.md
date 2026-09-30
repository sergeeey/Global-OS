# LH-COGNITIVE 48h — independent audit rubric (locked)

**Contour:** independent_lh_cognitive_48h_v1  
**Exam SHA:** `7ab345e5badb00a8c97ffdb7010ee4eb42dac4bb`  
**Protocol:** LH-COGNITIVE-v1

## Allowed reads

Freeze pack only: wall/preflight/smoke trees + FREEZE_META + MANIFEST.

## Hard gates (all required)

1. `fidelity == COGNITIVE_WALL_CLOCK_48H`
2. `wall_seconds >= 172800`
3. `m15_claimed == false` in report
4. `git_sha == 7ab345e…` (full freeze SHA)
5. `workload_class == EXTERNAL_RESEARCH_OBJECT`
6. top-level `passed == true` and all criteria passed
7. LOCKED_OBJECT + TERMINAL_REVIEW_PACK + ≥5 evidence JSON
8. supporting cognitive preflight report present and passed
9. freeze MANIFEST present

## Explicit non-claims even if all gates PASS

- production security / distributed exactly-once
- Continual SI
- causal GOS advantage vs strong baseline
- universal reliability outside protocol scope

## Outputs

- `m15_recommendation`: `M1.5_CANDIDATE_SCOPE_LIMITED` | `M1.5_NOT_CLAIMED`
- `m15_claimed_by_auditor`: always `false`
