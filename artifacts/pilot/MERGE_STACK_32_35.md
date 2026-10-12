# Merge stack #32–#35 → integration #36 (operator strategy)

**Status:** CI green on integration tip — **human merge required**  
(ADR dogfood: no autonomous T0/T1 merge)  
**Integration branch:** `cursor/post-debt-integration-2907`  
**Integration PR:** [#36](https://github.com/sergeeey/Global-OS/pull/36) (Draft until human accepts)  
**Base tip:** `main` @ `2f73107` (DurableRunner #31)

## Operator recommendation (2026-10-12)

Do **not** start Challenge-GA exec now. Do **not** open a new wide architecture campaign.

Most valuable step: bring already-ready changes to a **coherent `main`**.

### Single merge strategy (pick one — not both)

| Strategy | Action | Notes |
|----------|--------|-------|
| **A — preferred** | Merge **#36** only | Already contains #32→#35 stack + post-debt P1. Close #32–#35 as superseded after #36 lands. |
| **B — sequential** | Merge #32→#33→#34→#35, then rebase #36 for **unique** P1-only delta | Do not treat #32–#35 and #36 as independent deliveries of the same organs/authority/Challenge lock. |

**Default for this pack:** Strategy A.

## What #36 includes

1. Cognitive organ contracts + HUMAN `awaiting_human` (#32)
2. Authority P0: token↔tool, approval token, parent grants (#33)
3. T3 A/B model-sensitivity + honesty (#34)
4. CHALLENGE-GA `PREREG_LOCKED` (#35)
5. Post-debt P1: grounding claim⊆passage · PACK-v2/v3 5-check integrity · C2 decision-coupled sensitivity · Challenge organ fixture loop + exec gate

## Honesty layers (must stay distinct after merge)

| Layer | Claim strength |
|-------|----------------|
| Implemented mechanisms | Authority bind, organ *contracts*, HUMAN routing, PACK integrity |
| Working fixture loop | Decomposer→route→pivot + terminal scorer on naive fixture — **not** live Achiever |
| Full Autonomous Goal Achiever | **NOT SHOWN** until Challenge-GA terminal evidence |

Green CI on #36 proves the checks CI runs — **not** that organs can autonomously finish a hard real Goal.

## Post-merge checklist (human)

1. Combined tip verification: authority negatives + T3 sensitivity + Challenge harness/gate
2. Canon sync: ROADMAP / honesty map / capability_matrix / README distinguish the three layers above
3. Challenge prep only (`artifacts/pilot/challenge_ga/CHALLENGE_PREP.md`) — **exec only after explicit human request**

## Boundaries (unchanged)

`ATTR=NOT_SHOWN` · `M2=CLOSED` · `PRODUCTION_PROVEN=0` · `CHALLENGE_EXEC=NOT_STARTED`
