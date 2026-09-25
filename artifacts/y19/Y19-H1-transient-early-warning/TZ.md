# Y19 — Transient early-warning in random Boolean networks

**Mission id:** Y19-H1  
**Protocol:** `Y19-H1-v1`  
**Status:** Scientific dogfood (not M1.5, not LH exam)  
**Freeze note:** `bfa58a0` remains an intermediate stable point; Y19 may produce fixes → new SHA → new freeze later.

## Scientific question (answer unknown a priori)

> **Y19-H1.** Before an observed long transient, do local spectral and sensitivity
> features of the early state contain out-of-sample predictive information that is
> **not** in simple baselines (active-bit activity, state entropy, system size N/K)?

We do **not** know whether this is true. Honest `REJECTED` / `INCONCLUSIVE` is success.

## Why this class (vs Y17)

| Prior | Class | Why not repeat |
|-------|--------|----------------|
| Y17-3 | Boolean causal clamp on known cell-cycle net | Confirmatory recompute |
| Y17-5 | ω→M1 OLS forecast | Different domain (RMT/GOE) |
| **Y19** | Early-warning of long transient on **generated** NK Boolean nets | New question; sealed holdout; competing explanations |

## Domain

- Family: random Boolean NK networks (`N ∈ {16,20,24}`, `K ∈ {2,3}`)
- Thousands of independent (network_seed, trajectory) cases
- Label: `long_transient = 1[steps_to_attractor > τ]` with locked `τ=10`
- Early window: first `W=6` states only (features must not use future)

## Competing hypotheses (exactly three)

1. **H_spectral (primary Y19-H1)** — spectral/sensitivity extras improve sealed-holdout Brier by MCID **and** survive N/K ablation.
2. **H_baseline_sufficient** — simple features already capture all OOS signal; candidate fails MCID.
3. **H_size_spurious** — candidate meets MCID only while N/K are present; size-ablated model fails MCID.

## Baseline vs candidate

```text
Baseline features:
  n, k, mean_activity, activity_std, state_entropy

Candidate = baseline +
  sensitivity (local Boolean flip sensitivity),
  spectral_high_energy (DFT high-frequency power of activity),
  activity_range
```

## Preregistration (locked before holdout decision)

- **Train seeds:** 1000–1179 (180 nets)  
- **Sealed holdout seeds:** 5000–5119 (120 nets) — disjoint from Y17 ranges  
- **Model:** ridge linear probability (stdlib); fit on train only  
- **Primary metric:** holdout Brier  
- **MCID:** `Brier_candidate ≤ 0.90 × Brier_baseline`  
- **Ablation:** same MCID required with N/K removed from candidate  
- **Class balance gate:** holdout needs ≥12 positives and ≥12 negatives else `INCONCLUSIVE`

### Decision rule

| Outcome | Condition |
|---------|-----------|
| **SUPPORTED** | MCID pass **and** size-ablation MCID pass |
| **REJECTED** | MCID fail |
| **INCONCLUSIVE** | balance fail **or** MCID pass but ablation fail |

No post-hoc change of τ / W / MCID / seeds after seeing holdout ratio.

## What Global OS must not know early

- Whether Y19-H1 is true
- Holdout labels / which hypothesis wins
- Any “right answer” supplied by the operator

## What Global OS must do

```text
Goal → competing hypotheses → preregistration → generate data →
train-only fit → sealed holdout → null/negative preservation →
deterministic verification → SUPPORTED|REJECTED|INCONCLUSIVE
```

Optional later (during a longer dogfood / future 48h on a **new** freeze): revoke a dataset shard, cut budget, process kill, provider outage — **without changing the scientific question**.

## Explicit non-goals

- Not Riemann / not “famous open problem theater”
- Not M1.5 closure
- Not Continual SI claim
- Not proof of general forecasting skill beyond this locked protocol

## Entry points

- Engine: `global_os.evals.research.y19_transient_early_warning`
- Mission: `artifacts/y19/Y19-H1-transient-early-warning/execute_mission.py`
- Tests: `tests/test_y19_transient_early_warning.py`

## Relation to Windows / LH

```text
Windows os_kill smoke on bfa58a0     — still useful (seconds)
Windows 96m preflight / literal 48h  — DEFERRED while Y19 dogfood runs
Y19 may invalidate bfa58a0 as freeze — expected if real bugs appear
```
