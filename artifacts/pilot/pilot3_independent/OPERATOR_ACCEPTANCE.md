# Operator acceptance — PILOT3-IND-ENG-v1

**Date (UTC):** 2026-10-12  
**Source:** operator review of sealed Arm D / DECISION after PR #27 merge (`a4fc558`)  
**Independent re-audit of PR artifacts by operator:** not claimed in this note

## Accepted terminals (do not soften)

```text
PILOT3              = TERMINAL
ATTR (C vs B)       = PROCESS_DISCIPLINE_SUFFICES
GOS incremental     = NOT_SHOWN
M2 (org superiority)= CLOSED  (not deferred-with-optimism; closed on current evidence)
PRODUCTION_PROVEN   = 0
```

C>A on EPI/ENG is accepted. C−B = 0 confirmed delta is accepted as **failure to show** architecture-beyond-discipline advantage in this experiment — not as proof of universal B≡C.

## Claim taxonomy (binding after Pilot 3)

| Class | Content |
|-------|---------|
| `VERIFIED_CURRENT_VALUE` | Disciplined workflow beats baseline A on audit quality; Global OS can run that workflow; Pilot 2 reached external merge + green CI |
| `PLAUSIBLE_POTENTIAL` | GOS as infrastructure for durable evidence, effect authorization, reproducibility, handoff, state control |
| `NOT_SHOWN` | That complex Global OS architecture is **required** vs a simpler agent with checklist + ledger + verification protocol |
| `SPECULATIVE_POTENTIAL` | Dynamic agent orgs, long-horizon compounding advantage, self-improvement — not supported by Pilot 3 |

## Engineering decision

```text
Next ≠ M2
Next ≠ architecture scale-up
Done: architecture ablation ARCH-ABLATION-MECH-v1 TERMINAL
Done: MINIMAL-STACK-v1 LOCKED (DEFAULT=G1+G2+G3; Gfull OPT-IN)
Next = dogfood DEFAULT stack under claim-boundary checklist
      (optional: Paperclip WI human; optional: higher-fidelity ATTR prereg)
```

ATTR negative result remains a claim-limiting invariant for product messaging.
See `artifacts/pilot/minimal_stack/MINIMAL_STACK_CONTRACT.md`.
