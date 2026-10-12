# Goal Contract — ARCH-ABLATION-MECH-v1

## Objective

Measure which minimal Global OS mechanism layers prevent sealed invariant breaks
beyond a disciplined mutable baseline (B0), under long / fault / handoff / effect
stress — without claiming Pilot 3 ATTR overturned.

## Success criteria

1. LOCK sealed before score interpretation.
2. All arms × scenarios executed by harness; SCOREBOARD written.
3. DECISION uses sealed vocabulary; preserves ATTR NOT_SHOWN and M2 CLOSED.
4. Acceptance tests green (`tests/test_arch_ablation.py`).

## Non-goals

```text
reopen M2
soften Pilot 3 ATTR
external WorldInteraction on Paperclip (optional separate track)
new Authority / Epistemic / OrgCompiler surfaces
PRODUCTION_PROVEN
LLM arm field study
```

## Invariants

- Proposal ≠ Effect (GOS-I13/I14)
- Goal immutability (GOS-I06)
- Append-only ledger (no silent erase of null results — GOS-I11)
- Child authority ⊆ parent (GOS-I04)
- No LLM boolean security decisions
