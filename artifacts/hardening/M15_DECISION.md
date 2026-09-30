# M1.5 decision — LH-COGNITIVE-v1 (scope-limited)

**Status:** DRAFT pending operator freeze+audit output  
**Exam SHA:** `7ab345e5badb00a8c97ffdb7010ee4eb42dac4bb`  
**Fill from:** `artifacts/hardening/audit_cognitive_48h/out/INDEPENDENT_REVIEW.json`

## Claim template (narrow)

> On frozen implementation `7ab345e`, in the fixed Windows test environment and within
> LH-COGNITIVE-v1 protocol scope, Global OS **did / did not** demonstrate the ability to
> run an EXTERNAL_RESEARCH_OBJECT cognitive research workload continuously for
> `wall_seconds >= 172800`, preserving stated Goal/Epistemic/Recovery integrity properties
> without mid-run modification of the runtime.

## Provisional (from operator harness report — not yet audit-locked)

| Gate | Harness observation |
|------|---------------------|
| fidelity | COGNITIVE_WALL_CLOCK_48H |
| wall_seconds | 172801.20 |
| m15_claimed | false |
| workload | EXTERNAL_RESEARCH_OBJECT |
| git_sha | 7ab345e… |

**Harness:** PASS  
**Independent audit:** PENDING (run `OPERATOR_POST_48H_NOW.md`)  
**M1.5 claimed:** **false** until audit JSON says `M1.5_CANDIDATE_SCOPE_LIMITED` and human confirms.

## Explicit non-claims

- production security / distributed exactly-once  
- Continual SI / universal reliability  
- causal GOS advantage vs strong baseline (H_TRUST still next)  
- durability sum-harness on `5d15600` ≠ this claim  

## Next after audit PASS

1. Lock this file to `CANDIDATE_ACCEPTED` or `NOT_CLAIMED`  
2. Activate post-M1.5 plan: `SAFE_AUTONOMY_BENCHMARK-v1` / Mission Assurance T1  
   (`NEXT_MECHANISM_MISSION_ASSURANCE.md`)
