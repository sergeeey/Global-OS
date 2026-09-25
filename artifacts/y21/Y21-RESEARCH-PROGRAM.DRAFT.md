# Y21 Research Program — Draft Prereg (not locked)

**Status:** DRAFT after Y20 · **Not started** · **Not locked**  
**Why:** Cross-domain transfer test + cleaner attribution than Y20.

## Motivation from Y20

Y20 showed no sealed-accuracy win for GOS loop vs strong baseline; process trace
was richer under GOS. Integrity caveat: generator author = arm runner.

Y21 must:
1. Use a **different cognitive class** (not causal/statistical synthetic).
2. Ensure baseline arm is run by a process that **never authored** the generator
   (separate worktree/agent or operator-sealed generator authored offline).

## Proposed task class (prefer)

**Algorithmic / combinatorial:** recover structure of a hidden discrete process
(e.g. unknown finite-state transducer or sorting-network fault localization)
from input/output traces; predict outputs on sealed holdout programs.

Alternative: physical/numerical ODE parameter + regime identification.

## A/B (same discipline as Y20)

Equal model, data, tools, budgets. A = strong agent ordinary workspace.
B = same model + GOS research loop. A→freeze→B→freeze→unseal→score.

## Non-goals

- Mutating Y20 scorer post hoc
- LH / M1.5 / Continual SI from Y21 alone
- Declaring universal GOS advantage

## Lock condition

This file becomes binding only after `Y21-PREREG.md` is committed with
`prereg_boundary_sha` and sealed generator authored without arm-runner access.
