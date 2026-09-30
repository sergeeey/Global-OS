# Y24-F2 — Locked protocol amendment (sample-size continuation)

**Status:** `AMENDMENT_LOCKED`  
**Protocol id:** `Y24-AVCT-v1-F2`  
**Parent:** `Y24-AVCT-v1`  
**Date (UTC):** 2026-09-30  
**Trigger:** fold-1 holdout MEDIUM/HIGH underpowered (N&lt;8) → INCONCLUSIVE

## Why this is a continuation, not “the same clean prereg”

Original `Y24-PREREG` allows **INCONCLUSIVE on underpowered N**, but does **not**
explicitly preregister a rule of the form:

> “if MEDIUM/HIGH holdout N&lt;8, enlarge sample to N≥8 and re-run under the same pack.”

Therefore fold-2 is **not** a silent continuation of a pristine sealed prereg.
It is a **locked protocol amendment / continuation**:

```text
Y24 fold-1  → HEURISTIC_HARNESS_v1 → INCONCLUSIVE → IMMUTABLE
Y24-F2      → corpus extension → blind strata → seal → hash → then A/B/C
```

## Locked amendment text

```text
protocol amendment (Y24-F2 / Y24-R1):
  increase MEDIUM/HIGH holdout N to >=8 due to underpowered fold-1
```

## Unchanged (MUST)

| Surface | Change? |
|---------|---------|
| KEEP / REJECT / INCONCLUSIVE decision rules | **No** |
| MCID numeric values | **No** |
| Complexity rubric / strata cutpoints | **No** |
| Cost accounting formula / COST_RATIO_MAX | **No** |
| Isolation gate | **No** |
| Arm A/B/C definitions | **No** |
| Trust Kernel / C2 / T3-as-evidence | **Forbidden** |

## Required process for Y24-F2

1. Fold-1 remains immutable under `artifacts/y24/fold1_immutable/` (+ sealed archive).
2. New MEDIUM/HIGH cases are a **corpus extension**, selected **blind to fold-1 arm outcomes**
   (no peeking at which tasks A/B/C escaped/blocked in fold-1).
3. Blind stratification with locked rubric → seal holdout → SHA256 → freeze experiment SHA.
4. Isolation attestation remains in force for C/memory builders vs sealed labels.
5. Only then unseal for execution → run A/B/C → decision.
6. Fidelity remains `HEURISTIC_HARNESS_v1` until a separate live-LLM fidelity upgrade is locked.
   Even a future KEEP under this harness is **not** live-LLM proof.

## Honesty about ordering on this branch

- Fold-1 was unsealed and scored before this amendment was named `Y24-F2`.
- An N-note existed before fold-2 seal/run, but calling it “same prereg” was **too strong**.
- This document **corrects the boundary**: Y24-F2 = locked amendment continuation.
- Fold-2 sealed pack hash and heuristic REJECT stand as **Y24-F2 evidence**, not as a
  rewrite of fold-1 and not as architecture failure requiring system edits.

## Non-claims

- Not Trust Kernel promotion
- Not production security
- Not live-LLM verification superiority
- INCONCLUSIVE/REJECT here ≠ “fix the architecture”
