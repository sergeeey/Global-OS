# NEXT — Architecture Ablation (post–Pilot 3)

**Status:** `PREREG_DRAFT`  
**Depends on:** PILOT3 TERMINAL · ATTR = NOT_SHOWN / PROCESS_DISCIPLINE_SUFFICES  
**Forbidden:** reopening M2; softening Pilot 3 ATTR; maturity bumps without new evidence

## Question

Which **minimal** Global OS mechanisms add measurable value beyond Arm B
(checklist + ledger + sealed repro), especially under:

```text
long-running tasks
faults / restarts
control handoffs
external-effect re-verification (Proposal ≠ Effect)
```

## Suggested arms (draft — lock later)

| Arm | Stack |
|-----|--------|
| B0 | Disciplined baseline (Pilot 3 Arm B protocol) |
| G1 | B0 + immutable Goal Contract + append-only ledger only |
| G2 | G1 + effect receipt / WorldInteraction gate |
| G3 | G2 + Authority/ToolGateway fail-closed path |
| Gfull | Full GOS process (Pilot 3 Arm C) |

Primary comparisons: **G\* vs B0**, not Gfull vs strong-A alone.

## Success rule

A G-arm wins only if it beats B0 on sealed EPI/ENG (and EFF if metered) beyond ATTR tolerance **without** fidelity breaks.  
Ties and B0 wins are valid scientific outcomes.

## Non-claims until locked/executed

```text
≠ component X is valuable
≠ M2 reopened
≠ PRODUCTION_PROVEN
```
