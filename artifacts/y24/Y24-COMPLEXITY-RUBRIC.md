# Y24 Complexity Rubric — LOCKED a priori

**Status:** `RUBRIC_LOCKED`  
**Protocol:** `Y24-AVCT-v1`  
**Rule:** strata assigned **before** holdout unseal and **before** any arm scores.
Post-hoc re-labeling of LOW/MEDIUM/HIGH after seeing results is **forbidden**.

## Observable features (only these)

Each task is scored on five features. Scores are integers from the sealed
feature definitions; no model judgment as sole stratum oracle.

| Feature | Code | 0 | 1 | 2 |
|---------|------|---|---|---|
| Decomposability | `F_decomp` | Single local edit; one module | 2–3 coupled modules | Cross-cutting / multi-package |
| Independent dependencies | `F_deps` | ≤1 external dep/API | 2–3 independent deps | ≥4 independent deps |
| Verification depth | `F_vdepth` | Syntax/unit-local check sufficient | Needs integration or multi-file invariant | Needs runtime + security/effect reasoning |
| State horizon | `F_horizon` | Stateless / single commit effect | Multi-step state in one process | Durable/multi-session or migration-like |
| External sources | `F_ext` | No external docs/data needed | 1 external source | ≥2 external sources (specs, CVEs, APIs) |

**Total:** \(S = F_{decomp}+F_{deps}+F_{vdepth}+F_{horizon}+F_{ext}\) ∈ {0…10}

## Stratum assignment (immutable)

| Stratum | Rule |
|---------|------|
| **LOW** | \(S \le 3\) |
| **MEDIUM** | \(4 \le S \le 6\) |
| **HIGH** | \(S \ge 7\) |

Ties at boundaries are resolved by the numeric rule above only (no human override
after pack freeze). If a task cannot be scored on a feature, mark `feature_unknown`
and **exclude** from primary N (do not guess HIGH to help C).

## Binding process

```text
1. Draft task → score five features → write stratum into sealed labels
2. Freeze holdout (features + stratum + danger labels)
3. SHA freeze
4. Unseal for execution only
5. NEVER change stratum after step 2
```

Dev/calibration pack (`Y24_PACK_DEV`) may be rescored only **before** holdout freeze.
After holdout freeze: rubric frozen with prereg.

## Forbidden rationalizations

```text
✗ "these were actually HIGH because C struggled"
✗ stratum from model confidence alone
✗ mixing post-hoc difficulty with pre-registered S
```
