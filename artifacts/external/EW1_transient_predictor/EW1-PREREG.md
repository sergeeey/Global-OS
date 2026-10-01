# EW1 — Chaotic Transient Early Predictor (science)

**Status:** `PREREG_LOCKED`  
**Protocol id:** `EW1-CTP-v1`  
**Mission id:** `EW1`  
**Date (UTC):** 2026-10-01

## Independence

- **Not** a reopen of frozen Y19 (NK Boolean transient program).
- Y19 / Y24 / Y25 results are **not** evidence for EW1 claims.
- Domain is different: continuous coupled maps, not Boolean NK nets.

## Scientific question (answer unknown)

> Does an early-window predictor of transition from a quasi-stable regime into a
> **long / chaotic transient** beat a strong simple baseline on a **sealed holdout**
> in a coupled logistic-map lattice?

Honest `REJECTED` / `INCONCLUSIVE` is a successful mission outcome.

## System

- Coupled logistic maps on a ring of size `N` (locked: `N ∈ {16, 24}`)
- Coupling `ε`, parameter `r` near the edge of chaos (locked ranges in JSON)
- Trajectory from random IC; early window first `W` steps only for features
- Label: `long_chaotic = 1` if steps-to-enter-sustained-chaos / return-time
  exceeds locked threshold `τ` (definition in `EW1-PREREG.json`)

## Competing hypotheses (exactly 3)

1. **H_early_complexity (primary)** — early permutation entropy / spectral high-freq
   extras improve sealed-holdout Brier vs baseline by MCID and survive size ablation.
2. **H_baseline_sufficient** — mean activity / variance / Lyapunov-proxy already
   capture all OOS signal; candidate fails MCID.
3. **H_size_spurious** — candidate only wins while `N` is in the model; fails ablation.

## Baseline vs candidate

```text
Baseline:
  N, mean_x, std_x, max_abs_dx

Candidate = baseline +
  permutation_entropy_early,
  spectral_high_energy,
  local_divergence_proxy
```

## Protocol locks

| Item | Lock |
|------|------|
| Train seeds | `1000–1299` |
| Holdout seeds | `9000–9149` (sealed; disjoint) |
| Model | ridge linear probability (stdlib) / equivalent documented |
| Primary metric | holdout Brier |
| MCID | `Brier_candidate ≤ 0.90 × Brier_baseline` |
| Ablation | same MCID without `N` |
| Class balance | holdout ≥12 pos and ≥12 neg else `INCONCLUSIVE` |

## Decision

- **SUPPORTED** if primary + ablation MCID on sealed holdout
- **REJECTED** if powered and fails
- **INCONCLUSIVE** if underpowered / integrity / env block

## Forbidden

- Peek holdout labels before seal/unseal gate
- Post-hoc feature mining after unseal
- Cite Y19-H1 spectral story as EW1 evidence
- Change Global OS to “help” the score

## Artifacts

- `EW1-PREREG.json` — machine-readable locks
- `sealed/` — holdout seed manifest (empty until generated+sealed)
- Runner / data generators — eval harness only (no Trust Kernel)
