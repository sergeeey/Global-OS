# M-EXT5 — TERMINAL DECISION

**Protocol:** `M-EXT5-INIT-MPEMBA-v1`  
**Status:** `CAMPAIGN_CLOSED`  
**Date (UTC):** 2026-10-02

## Dual terminals

| Hypothesis | Endpoint | Result |
|------------|----------|--------|
| **H_EFFECT** (primary) | τ to train CE ≤ **0.35** (late / final-regime) | **REJECTED** |
| **H_EFFECT_EARLY** (secondary) | τ to train CE ≤ **1.0** | **SUPPORTED_WITHIN_SCOPE** |
| **H_FISHER** | early grad-norm proxy, conditional on primary | **REJECTED** |

```text
n_valid = 20 / 20
n_wins_late  = 2   → REJECTED (≤12 rule; far from 15)
n_wins_early = 20  → SUPPORTED_WITHIN_SCOPE (secondary only)
H_FISHER     = REJECTED (primary effect absent)
```

## Meaning

Under locked primary definition aligned with a **late** loss target (near final regime),
initialization-induced Mpemba-like advantage of hot over cold is **not** supported:
cold reaches the late target sooner on 18/20 sealed pairs.

A **threshold-dependent** early crossing (hot reaches mid loss≤1.0 sooner) is real
under the secondary preregistered endpoint, but **does not** promote H_EFFECT primary
and is **not** evidence for Fisher geometry (H_FISHER REJECTED).

```text
observed early crossing  ≠  late-regime Mpemba
observed early crossing  ≠  Fisher mechanism
```

## Scope

Synthetic 2-layer MLP, fixed LR vanilla SGD, identical batches, CPU.  
Not LLM / not MNIST (torchvision broken in env). Within-protocol only.

## Integrity

- Mechanical gate GREEN before confirmatory  
- Stats rule 15/20 (not M-EXT4’s broken 14/20)  
- Seal SHA256 in `PREREG.json`  
- M-EXT4 not rewritten  
- GOS architecture unchanged  

## Raw

`artifacts/external/EW5_init_mpemba/results/confirmatory_results.json`
