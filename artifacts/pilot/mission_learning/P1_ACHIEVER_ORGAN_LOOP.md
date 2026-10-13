# P1 — Achiever organ loop (Contour A)

**Status:** HARNESS_WIRED (not PRODUCTION_PROVEN)  
**Branch:** `cursor/achiever-organ-loop-2907`  
**Code:** `src/global_os/cognition/organs/achiever_loop.py`

## Control flow

```text
Goal → Decomposer → Orchestration → attempt_fn → Completion Gate
                 ↑                         |
                 └──── Pivot (budget) ─────┘
```

- Completion Gate decides `ACHIEVED` / `PARTIAL` / `FAILED` / `UNKNOWN`
- `challenge_win_claimed` always false here (Challenge exec is separate)
- No world effects inside the loop (Gateway required for material actions)

## Wiring

- Challenge fixture loop binds sealed scorer → Completion Gate
  (`evals/challenge_ga/completion_bind.py`)
- Naive fixture → ops unmet → not ACHIEVED

## Skill Transfer Trial

- `prepare_skill_transfer_trial` fail-closed while Challenge ≠ COMPLETED
- Continual SI remains NOT_MEASURED

## Boundaries

`ATTR=NOT_SHOWN` · `M2=CLOSED` · `PRODUCTION_PROVEN=0` ·  
`CHALLENGE_EXEC=NOT_STARTED` · `CONTINUAL_SI=NOT_MEASURED`
