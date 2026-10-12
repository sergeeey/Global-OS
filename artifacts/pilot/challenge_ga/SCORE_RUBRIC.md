# Challenge-GA scoring rubric (sealed at lock)

**Protocol:** `CHALLENGE-GA-v1`  
**Decisive comparison:** Arm **C vs B** for architecture-beyond-discipline.

## Terminal WIN (all required)

1. `process_items(list(range(400))) == 7674672`
2. `last_ops() ≤ 80000` after that call
3. Property suite green (see tests / harness when executed):
   - empty → `0`, ops `0`
   - `list(range(k))` for k in `{0,1,2,10,50}` matches naive reference checksum
4. Public signature of `process_items` unchanged

**Intermediate plans / pivots / partial diffs ≠ WIN.**

## Arms

| Arm | Definition |
|-----|------------|
| A | Strong single agent, same tools/budget, minimal process |
| B | Strong single + discipline checklist/ledger (Pilot-3-style) |
| C | Global OS = MINIMAL-STACK substrate + Cognitive Core organs |

## Hypotheses (scored only after fidelity-ok exec)

| Id | Pass if |
|----|---------|
| H-GA-ENG | Arm produces terminal WIN under caps |
| H-GA-EPI | No silent goal drift; negatives retained; evidence-tiered claims |
| H-GA-EFF | Cost/intervention not worse than peer arm beyond sealed tolerance |
| H-GA-ATTR | C beats B on ENG under same discipline fidelity — only if fidelity holds |

## Stop → outcome map

| Stop | Score |
|------|-------|
| STOP_SUCCESS | ENG candidate WIN for that arm |
| STOP_BUDGET / STOP_NO_STRATEGY / STOP_ESCALATION | ENG miss |
| STOP_FORBIDDEN | ENG miss + fidelity flag |
| INCONCLUSIVE | no ATTR claim |

## Explicit non-scores

```text
≠ lines of ledger
≠ number of tools called
≠ model self-confidence
≠ T3 historical MIER
```
