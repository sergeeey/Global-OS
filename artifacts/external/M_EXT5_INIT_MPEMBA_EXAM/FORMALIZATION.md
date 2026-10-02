# M-EXT5 — Formalization & endpoints

**Status:** `LOCKED_WITH_PREREG`  
**Scope:** synthetic 2-layer MLP (CPU); torchvision unavailable in env — documented.

## H_EFFECT primary (LATE)

```text
At t=0: D_L2(θ_hot, θ_ref) > D_L2(θ_cold, θ_ref)
τ = first step with batch CE loss ≤ 0.35
Hot wins if τ_hot < τ_cold
```

- `θ_ref`: reference net trained `ref_train_steps=4000` with seed `ref_seed`.  
- Init: σ = factor × H_e, H_e = √(6/fan_in); hot factor=2.0, cold=0.3.  
- Dynamics: identical precomputed batch stream; vanilla SGD, fixed LR.  
- Primary statistic: among valid pairs, n_wins_late; need ≥15/20, p<0.05 one-sided Bin(n,0.5).

## H_EFFECT secondary (EARLY) — cannot alone claim primary SUPPORT

Same construction; τ at loss ≤ 1.0. Reported as `H_EFFECT_EARLY_SECONDARY`.

## H_FISHER (mechanistic secondary)

Cheap proxy only: early (first 20 steps) mean gradient L2 norm.  
Test whether hot > cold on the same valid pairs with the same 15/20 rule.  
**Not** a Fisher–Rao geodesic. Absolute Fisher geometry not claimed.

## Explicitly rejected as primary

- Unspecified KL(θ, θ*)  
- M-EXT4 broken 14/20 α rule  
- Uncalibrated P≈0.6 language  
