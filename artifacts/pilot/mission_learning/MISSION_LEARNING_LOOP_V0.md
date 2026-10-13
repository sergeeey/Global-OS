# Mission Learning Loop v0

**Status:** HARNESS_ONLY  
**ADR:** ADR-0014  
**Trust zone:** T2 / eval — no T0/T1 surfaces  
**Continual SI:** NOT_MEASURED

## Mission alignment

Self-improvement helps the Autonomous Goal Achiever. It is not a self-goal.

## Scope

```text
1 mission archived
→ 1 failure_class diagnosed
→ 2 unprivileged candidates + baseline
→ same-suite sandbox scores (incl. losses)
→ promotion = REQUIRES_HUMAN always
```

## Success criterion (v0)

An improvement is interesting only if it is:

- **repeatable** under fixed budget,
- **non-regressive** vs parent on the suite,
- **transfer-aware** fields present (holdout suite id recorded; may be NOT_RUN),
- **cost-aware** (complexity budget + deletion_test fields).

Not success: “model sounded smarter” / LLM self-grade alone.

## Contours

| Contour | v0 |
|---------|----|
| A Goal Achievement | Prerequisite track — see `P1_ACHIEVER_GATE.md` |
| B Experience Evolution | **This loop** |
| C Challenge Evolution | Deferred; Challenge-GA ≠ train set |

## Non-claims

```text
≠ L4/L5 RSI
≠ Continual SI measured
≠ transferable skill library with applicability conditions
≠ Authority / scorer self-mod
≠ Challenge-GA trained or executed
≠ auto-promotion into runtime
```

## Boundaries

`ATTR=NOT_SHOWN` · `M2=CLOSED` · `PRODUCTION_PROVEN=0` ·
`CHALLENGE_EXEC=NOT_STARTED` · `CONTINUAL_SI=NOT_MEASURED`
