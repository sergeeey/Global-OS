# DECISION — ARCH-ABLATION-MECH-v1

**Status:** `TERMINAL`  
**Date (UTC):** 2026-10-12  
**Fidelity:** `SCRIPTED_MECHANISM_ABLATION`  
**Harness:** `src/global_os/evals/research/arch_ablation.py`  
**Score:** `score/SCOREBOARD.json`  
**Tests:** `tests/test_arch_ablation.py` (fail-closed semantics + scoreboard; see CI)

## Parent invariants (frozen — not softened)

```text
Pilot 3 ATTR (C vs B)     = PROCESS_DISCIPLINE_SUFFICES
GOS incremental (Pilot 3) = NOT_SHOWN
M2 (org superiority)      = CLOSED
PRODUCTION_PROVEN         = 0
```

This pack answers a **different** question (mechanism discrimination under scripted
stress). Positive mechanism results **do not** overturn Pilot 3 ATTR on LLM audit EPI/ENG.

## Scoreboard (scenarios held / 4)

| Arm | Held | Unique vs B0 | Wins vs B0 |
|-----|------|--------------|------------|
| B0 | 0 | — | — |
| G1 | 2 (S1,S2) | S1,S2 | yes |
| G2 | 3 (S1,S2,S4) | S1,S2,S4 | yes |
| G3 | 3 (S1,S2,S4) | S1,S2,S4* | yes |
| Gfull | 4 | S1–S4 | yes |

\*G3 additionally denies privilege expansion on S3 (G1/G2 do not) but still loses
S3 full invariant on handoff info-loss; only Gfull holds S3 completely.

## Hypotheses

| Id | Verdict |
|----|---------|
| H-ABL-G1 | `SUPPORTED` — immutable Goal + append-only ledger catch silent mutation / negative erasure |
| H-ABL-G2 | `SUPPORTED` — EffectReceipt catches ToolSuccess≠WorldSuccess (G1 does not) |
| H-ABL-G3 | `SUPPORTED` — Authority fail-closed denies privilege expansion (G2 does not) |
| H-ABL-Gfull | `SUPPORTED` — G3 + DurableRunner resume + artifact handoff holds all four |
| H-ABL-ATTR-PRESERVE | `SUPPORTED` — Pilot 3 ATTR / M2 CLOSED restated; not reopened |

## Interpretation (binding)

```text
VERIFIED_CURRENT_VALUE (this fidelity):
  Specific GOS mechanism layers prevent sealed invariant breaks that a mutable
  disciplined baseline (B0) misses — layered as G1→goal/ledger, G2→effect,
  G3→authority, Gfull→durable+artifact handoff.

NOT_SHOWN (still):
  That full GOS is required for LLM audit quality vs Pilot 3 Arm B discipline.
  Org/topology superiority (M2).
  PRODUCTION_PROVEN.

PLAUSIBLE_POTENTIAL:
  Product focus on Goal immutability, append-only evidence, effect reconciliation,
  and fail-closed authority — without claiming recursive-org advantage.
```

## Engineering implications

1. Keep Pilot 3 ATTR as claim-limiting for audit-product messaging.
2. Prefer **minimal mechanism stack** justified by failure class (not Gfull by default).
3. Do **not** reopen M2; optional later ablation at higher fidelity (distinct providers)
   requires a new prereg.
4. Optional separate track: Paperclip external fix WorldInteraction (human gate).

## Non-claims

```text
≠ Pilot 3 ATTR overturned
≠ M2 reopened
≠ PRODUCTION_PROVEN
≠ LLM field superiority
≠ new T0/T1 architecture surfaces (ADR-0009 honored — eval harness only)
```
