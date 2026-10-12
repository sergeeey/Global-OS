# NEXT — Architecture Ablation (post–Pilot 3)

**Status:** `SUPERSEDED_BY_EXECUTION`  
**Active pack:** `artifacts/pilot/arch_ablation/` (`ARCH-ABLATION-MECH-v1` TERMINAL)  
**Depends on:** PILOT3 TERMINAL · ATTR = NOT_SHOWN / PROCESS_DISCIPLINE_SUFFICES  
**Forbidden:** reopening M2; softening Pilot 3 ATTR; maturity bumps without new evidence

## Outcome (scripted mechanism ablation)

See `artifacts/pilot/arch_ablation/DECISION.md`.

```text
H-ABL-G1/G2/G3/Gfull = SUPPORTED (SCRIPTED_MECHANISM_ABLATION)
Pilot 3 ATTR         = NOT_SHOWN (preserved)
M2                   = CLOSED (preserved)
PRODUCTION_PROVEN    = 0
```

Mechanism layers catch sealed invariant breaks B0 misses (goal/ledger → effect →
authority → durable+artifact handoff). This does **not** overturn Pilot 3 ATTR
on LLM audit quality.

## Historical draft arms (now locked in arch_ablation/)

| Arm | Stack |
|-----|--------|
| B0 | Disciplined baseline (mutable goal/ledger stand-in) |
| G1 | Immutable Goal Contract + append-only ledger |
| G2 | G1 + effect receipt / WorldInteraction gate |
| G3 | G2 + Authority/ToolGateway fail-closed |
| Gfull | G3 + DurableRunner + artifact-first handoff |

Primary comparisons: **G\* vs B0**, not Gfull vs strong-A alone.
