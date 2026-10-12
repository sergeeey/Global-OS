# PREREG — ARCH-ABLATION-MECH-v1

**Status:** `LOCKED` (see `LOCK.json`)  
**Protocol id:** `ARCH-ABLATION-MECH-v1`  
**Parent program:** post–Pilot 3 architecture ablation  
**Primary comparisons:** each G-arm vs B0 (not Gfull vs strong-A)

## Hypotheses

| Id | Claim |
|----|--------|
| H-ABL-G1 | G1 beats B0 on S1 and S2 (goal immutability + append-only retention) |
| H-ABL-G2 | G2 beats B0 (and G1) on S4 (effect reconciliation) |
| H-ABL-G3 | G3 beats B0 (and G1/G2) on S3 privilege-expansion (authority fail-closed) |
| H-ABL-Gfull | Gfull ≥ G3 on all sealed scenarios; may uniquely hold S3 info-loss / durable resume |
| H-ABL-ATTR-PRESERVE | Pilot 3 ATTR remains NOT_SHOWN; this pack does not reopen M2 |

## Lock sequence

```text
1. Seal this PREREG + METRICS + SCENARIOS + FIDELITY
2. Seal LOCK.json (arms, scenarios, tolerance, fidelity, tip SHA)
3. Implement/execute scripted harness (no LLM arms)
4. Emit score/SCOREBOARD.json from harness
5. Write DECISION.md; preserve ATTR / M2 CLOSED
```

Amendments after lock require `PREREG_AMENDMENT.md` **before** score unseal.

## Ordered evaluation

Per G-arm vs B0:

```text
1. No fidelity break (harness must run all sealed scenarios for all arms)
2. Count scenarios where invariant_held=true
3. G-arm wins iff wins_vs_B0 ≥ 1 beyond tolerance AND no G-arm unique invariant break
   that B0 also holds on the same scenario class
4. Mechanism attribution: win must map to the arm's added stack layer
   (G1≠effect, G2≠authority, etc.) — else INCONCLUSIVE for that hypothesis
```

Tolerance: absolute scenario-count delta ≥ 1 (n=4 sealed scenarios; no % fudge).

## Terminal vocabulary

| Verdict | Meaning |
|---------|---------|
| `SUPPORTED` | Hypothesis holds under ordered eval + fidelity |
| `REJECTED` | Opposing pattern dominates |
| `TIE` | Equal invariant_held counts |
| `NOT_SHOWN` | Advantage claim not justified |
| `INCONCLUSIVE` | Fidelity break or attribution mismatch |

## Forbidden after lock

```text
soften Pilot 3 ATTR / claim GOS incremental on Paperclip audit EPI
reopen M2 org superiority from this pack alone
mark PRODUCTION_PROVEN
add new T0/T1 architecture surfaces (ADR-0009)
LLM boolean security decisions inside harness
silent fallback to allow on authority/effect paths
discard negative mechanism results
```

## Relationship to Pilot 3

```text
Pilot 3 ATTR (C vs B, LLM audit) = PROCESS_DISCIPLINE_SUFFICES / NOT_SHOWN
This pack asks a different question:
  which mechanisms prevent sealed invariant breaks under scripted stress?
Positive mechanism results ≠ Pilot 3 ATTR overturned.
```
