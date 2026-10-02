# PREREGISTRATION — M-EXT4 Mpemba Effect in NN Parameter Dynamics

**Exam:** `M-EXT4-MPEMBA`  
**Protocol:** `M-EXT4-MPEMBA-v1`  
**Status:** `PREREGISTRATION_LOCKED`  
**Registered:** 2026-10-01T19:45:00Z  
**Agent:** autonomous agent executing M-EXT4 mission  
**Lock rule:** This document becomes **IMMUTABLE** upon pilot completion. No post-hoc endpoint changes after confirmatory unseal.

---

## 1. Research Question

**Primary:**  
Does there exist a Mpemba-like relaxation effect in neural network training whereby a parameter state initially **farther** from a pre-defined converged state, under **identical** subsequent SGD dynamics, reaches that state **earlier** than a state initially closer?

**Secondary (mechanistic):**  
Is the effect (if present) linked to **loss-landscape curvature geometry** (Hessian/Fisher structure) rather than trivial initial-loss differences?

---

## 2. Background & Motivation

### Prior work:
- **Liu & Hu (2025, arxiv:2507.04206):** Claimed Mpemba effect in LLM training via **LR-schedule manipulation** (high vs low plateau LR in warmup-stable-decay schedule). Theoretical framework (valley-river landscape, Fokker-Planck spectral analysis). **Acknowledged limited empirical validation.**
- **Warm-start literature (Ash&Adams 2020, DASH 2024):** Initialization variance affects convergence speed and generalization. High-variance (warm) converges faster but generalizes worse. **Not framed as Mpemba effect.**
- **Fisher geometry in DNNs (Karakida 2019, Jastrzebski 2021):** Loss landscape is anisotropic (sharp valleys, flat rivers). Fisher matrix structure affects training dynamics.

### Novelty of this study:
1. **Initialization-based construction** (not LR-schedule-based): Test hot/cold via parameter perturbation at **fixed LR**.
2. **Preregistered falsification test**: Liu&Hu did not run confirmatory protocol with competing-explanation controls.
3. **Small controlled setting**: 2-layer MLP on MNIST (vs LLM assumptions in Liu&Hu).
4. **Test-set endpoint**: Address overfitting concern (train-test mismatch).

### Outcome uncertainty:
- **SUPPORTED:** Mpemba effect confirmed in init-based setting → extends Liu&Hu to new construction.
- **REJECTED:** Effect absent → Liu&Hu effect may be LR-schedule-specific, not general parameter-dynamics phenomenon.
- **ILL_POSED:** Definitions infeasible or effect is coordinate artifact.

---

## 3. Hypotheses

### H1 (Mpemba effect — primary):
For a pair of initial states (θ_hot(0), θ_cold(0)) with D(θ_hot(0), θ*) > D(θ_cold(0), θ*), trained with identical SGD dynamics (same batches, same optimizer), the hot state reaches target region R* **faster**: τ_hot < τ_cold.

### H1_null:
No systematic difference: P(τ_hot < τ_cold) = 0.5 (hot and cold equally likely to win).

### H2 (Curvature mechanism — secondary):
The Mpemba effect (if H1 supported) is **not** explained by initial loss difference alone. Negative control (same loss, same curvature) does **not** exhibit crossing.

### H2_null:
Crossing occurs in negative control → initial loss difference sufficient, curvature geometry irrelevant.

---

## 4. Experimental Design

### 4.1 Architecture & Dataset
- **Model:** 2-layer MLP, width 128, ReLU activation
  ```
  Input (784) → Linear(128) → ReLU → Linear(10) → Softmax
  ```
- **Dataset:** MNIST (60k train, 10k test)
- **Loss:** Cross-entropy
- **Metric:** Classification accuracy

### 4.2 Reference State θ*
**Procedure:**
1. Train one reference run with random initialization (Kaiming uniform) until convergence:
   - Optimizer: SGD, LR=0.01, no momentum
   - Batch size: 128
   - Stop criterion: Train loss < 0.01 OR 10,000 steps (whichever first)
2. Save final parameters θ_ref.
3. Define θ* = θ_ref (reference target state).

**Pre-computed scale:**
- Compute H_e = mean of layer-wise Kaiming init scales: H_e = mean(σ_l) where σ_l = sqrt(2 / fan_in_l).
- Expected: H_e ≈ 0.16 for this architecture (L1: sqrt(2/784)≈0.05, L2: sqrt(2/128)≈0.125 → mean≈0.09; using safe estimate 0.1 ± inflation).

### 4.3 Hot & Cold Initialization
**Construction:**
- Sample θ_hot ~ N(θ*, σ_hot^2 I) where σ_hot = 2.0 * H_e.
- Sample θ_cold ~ N(θ*, σ_cold^2 I) where σ_cold = 0.3 * H_e.
- **Initial condition check:** Compute D(θ_hot(0), θ*) and D(θ_cold(0), θ*). If D_hot ≤ D_cold, **resample** (up to 5 attempts, else discard seed).

**Distance metric (two versions):**

**V1 (Primary — KL-based):**
```
D_KL(θ, θ*) = E_{(x,y) ~ S_calib} [ KL( p(y|x, θ*) || p(y|x, θ) ) ]
```
- S_calib = 1,000 randomly sampled points from train set (fixed, same for all experiments).
- KL(p || q) = Σ_i p_i log(p_i / q_i).
- Compute via forward pass: softmax outputs from θ* and θ on S_calib, average KL.

**V2 (Secondary — L2-based, for pilot exploration):**
```
D_L2(θ, θ*) = ||θ - θ*||_2
```
- May be reparametrization-dependent (checked via control C7).

**Target set:**
- Compute D_rand = D(θ_rand, θ*) where θ_rand = random Kaiming init.
- Define ε = 0.1 * D_rand (target is 10% of random-init distance from θ*).
- R* = {θ : D(θ, θ*) < ε}.

### 4.4 Training Protocol (Identical Dynamics)
- **Optimizer:** Vanilla SGD, **no momentum**, fixed LR η = 0.01
- **Batch size:** 128
- **Batch order:** Fixed shuffle seed S_data (same batches in same order for hot and cold within each run).
- **Max steps:** T_max = 5,000 (expected sufficient for convergence in this setting).
- **Monitoring:** Record D_hot(t), D_cold(t), L_train_hot(t), L_train_cold(t), L_test_hot(t), L_test_cold(t) every 10 steps.

### 4.5 Primary Endpoint
**First-passage time (test set):**
- Define τ_hot = min { t : D_test(θ_hot(t), θ*) < ε }
- Define τ_cold = min { t : D_test(θ_cold(t), θ*) < ε }
- **Primary comparison:** τ_hot < τ_cold ? (YES = hot wins, NO = cold wins or tie)

**Test-set distance:**
- D_test(θ, θ*) computed on **held-out test set** (MNIST test 10k), same as D but evaluated on test data.
- Rationale: Avoid overfitting artifact (C5 competing explanation).

### 4.6 Secondary Endpoints
1. **Train-set crossing:** Does crossing occur on train set? (D_train_hot < D_train_cold at some t)
2. **Loss crossing:** Does train loss cross? (L_train_hot < L_train_cold at some t)
3. **Sustained crossing:** After first crossing t_cross, does D_hot < D_cold persist for ≥50 steps?

---

## 5. Sample Size & Power

### Pilot phase (exploratory, open):
- **N_pilot = 5 seed pairs** (θ_hot^i, θ_cold^i, S_data^i) for i=1..5.
- **Purpose:** Feasibility check, estimate effect size, debug protocol.
- **Decision:** If ≥3/5 seed pairs show τ_hot < τ_cold → proceed to confirmatory. Else → REJECTED (underpowered → increase N or abandon).

### Confirmatory phase (sealed):
- **N_confirm = 20 seed pairs** (θ_hot^i, θ_cold^i, S_data^i) for i=1..20.
- **Holdout seal:** Seed values sealed in `SEALED_HOLDOUT.json` (SHA256 hash recorded) before pilot. Unseal only after pilot decision.
- **Power calculation:**
  - H0: P(win) = 0.5 (no effect).
  - H1: P(win) = 0.7 (Mpemba effect present, 70% win rate).
  - Binomial test, α=0.05, one-tailed.
  - Required wins: ≥14/20 (p=0.036 under H0, significant).
  - Power: P(X ≥ 14 | p=0.7) ≈ 0.75 (acceptable for exploratory study).

---

## 6. Competing Explanation Controls

### C1: Batch Order Effect
**Control:** For each confirmatory seed pair, repeat with K_batch=5 different batch shuffle seeds.
**Success criterion:** Hot wins in ≥4/5 batch orders → robust. Otherwise → batch-order artifact → exclude pair.

### C2: Random Seed Luck
**Built-in:** N=20 independent seed pairs. Binomial test aggregates across seeds.

### C3: Momentum Artifact
**Design choice:** Use vanilla SGD (no momentum) → rules out C3 by construction.

### C4: Initial Loss (Trivial Mechanism)
**Negative control:** Select 5 random winning pairs from confirmatory. For each:
1. Construct θ_hot_NC and θ_cold_NC by perturbing θ* along **same low-curvature direction** (smallest Hessian eigenvector v_min):
   - θ_hot_NC = θ* + α_hot * v_min
   - θ_cold_NC = θ* + α_cold * v_min
   - Tune α_hot, α_cold to match L(θ_hot_NC) ≈ L(θ_hot), L(θ_cold_NC) ≈ L(θ_cold).
2. Train both with same protocol.
3. Check: τ_hot_NC < τ_cold_NC ?

**Success criterion:** Crossing fails in ≥3/5 negative-control pairs → curvature mechanism supported.

### C5: Overfitting Artifact
**Primary endpoint is test-set crossing** → rules out C5 by construction.
**Secondary check:** Compare train vs test crossing direction. If opposite → overfitting → REJECTED.

### C6: Adaptive LR
**Design choice:** Fixed LR (no schedule) → rules out C6 by construction.

### C7: Coordinate Artifact (for V2)
**Reparametrization check:** Select 5 winning pairs. Apply reparametrization R (scale layer 1 by 2, layer 2 by 0.5). Recompute D_L2 under R. Check if crossing persists.
**Success criterion:** ≥4/5 persist → V2 robust. Otherwise → V2 is coordinate artifact → ILL_POSED for V2, revert to V1.

### C8: Edge-of-Stability Interaction
**Diagnostic:** Monitor largest Hessian eigenvalue λ_max(t) every 100 steps (Lanczos approximation, 50 iterations).
**Check:** Is λ_max_hot ~ 2/η = 200 (EoS signature)? If yes, flag EoS interaction (limitation).

### C9: Multi-Modality
**Exclusion criterion:** After T_max steps, check |L_hot(T) - L_cold(T)| < 0.05. If not, **exclude pair** (different basins).
**Abort criterion:** If >50% of pairs excluded → loss landscape too multi-modal → terminal ILL_POSED.

### C10: Implicit Regularization
**Exploratory (not primary):** Optionally repeat with explicit L2 reg (λ_reg=0.01). Check if crossing persists.

---

## 7. Statistical Analysis Plan

### Primary analysis:
```
Let W_i = 1 if τ_hot_test^i < τ_cold_test^i (hot wins on test set), else 0.
Filter: Exclude pairs failing C9 (multi-modality) or C1 (batch robustness).
Let n_valid = number of valid pairs (expect ≥10).
Let n_wins = Σ W_i (over valid pairs).

Binomial test (one-tailed):
  H0: P(win) = 0.5
  H1: P(win) > 0.5
  Threshold: n_wins ≥ 0.7 * n_valid (p < 0.05 significance level, approximate).

If n_wins ≥ 14 AND n_valid ≥ 20 → SUPPORTED.
If n_wins < 14 OR n_valid < 10 → REJECTED or ILL_POSED (depending on reason).
```

### Secondary analysis:
- **Effect size:** Median Δτ = median(τ_cold - τ_hot) over winning pairs. Report with 95% bootstrap CI.
- **Train-test agreement:** Correlation between train-crossing and test-crossing across pairs. If ρ < 0.5 → weak generalization.
- **Negative control (C4):** Binomial test on 5 NC pairs: n_NC_wins ≤ 1 (expect crossing to fail in ≥4/5). If n_NC_wins ≥3 → trivial mechanism, C4 supported → Mpemba mechanism unclear.

---

## 8. Falsification Criteria (Terminal Outcomes)

### SUPPORTED_WITHIN_SCOPE:
1. Primary: n_wins ≥ 14/20 (or ≥0.7 * n_valid) on test set, binomial p < 0.05.
2. Batch robustness (C1): Valid pairs pass ≥4/5 batch orders.
3. Negative control (C4): Crossing fails in ≥3/5 NC pairs (curvature mechanism).
4. Train-test agreement (C5): Test crossing present (not overfitting artifact).
5. (For V2) Reparametrization robust (C7): ≥4/5 pairs persist.

### REJECTED:
1. n_wins < 0.7 * n_valid (p ≥ 0.05) → no systematic Mpemba effect.
2. OR: Train crossing present but test crossing absent (overfitting artifact, C5).
3. OR: Negative control shows crossing (n_NC_wins ≥3/5) → trivial mechanism (C4).

### ILL_POSED:
1. n_valid < 10 after exclusions (loss landscape multi-modal, C9).
2. OR: (V2) Reparametrization check fails (≤2/5 robust) AND V1 infeasible (KL computation too expensive).
3. OR: θ* definition fails (reference run does not converge, or L(θ_ref) > threshold).

### INCONCLUSIVE:
1. Weak effect: n_wins ~ 12-13 (borderline significance).
2. OR: Effect present but dominated by EoS interaction (C8): ≥50% winning pairs have λ_max ~ 2/η.
3. OR: Pilot shows n_wins=2 or 3 (too weak to justify confirmatory cost).

---

## 9. Pre-Planned Amendments (Allowed)

**Before confirmatory unseal:**
- **Batch-order sample size:** If pilot suggests high batch-order sensitivity, increase K_batch from 5 to 10 (requires amendment record).
- **Distance metric switch:** If V2 (L2) pilot fails C7 and V1 (KL) pilot succeeds, lock to V1 for confirmatory (record reason).
- **Exclusion threshold (C9):** If pilot shows different-basin rate >20%, tighten exclusion to |L_hot - L_cold| < 0.02 (record amendment).

**Forbidden post-confirmatory:**
- **Endpoint change:** Cannot switch from test-set τ to train-set τ after confirmatory unseal.
- **Metric change:** Cannot switch from KL to L2 (or vice versa) after unseal.
- **Threshold tuning:** Cannot adjust n_wins threshold (≥14) after unseal.
- **Seed fishing:** Cannot cherry-pick "good" seeds from sealed set.

---

## 10. Timeline & Resources

### Estimated compute:
- **Pilot (5 seed pairs, 5 batch orders each = 25 runs):**
  - Each run: 5,000 steps * 128 batch * forward+backward ≈ 10-15 min on CPU (MLP is small).
  - Total pilot: ~6-8 hours.
- **Confirmatory (20 seed pairs, 5 batch orders each = 100 runs):**
  - Total: ~30-40 hours on single CPU.
  - **Parallelization:** Can run 4-8 seeds in parallel if multi-core available → wall-clock ~8-12 hours.
- **Negative control (5 pairs):** +2 hours.
- **Sharpness monitoring (C8):** +20% overhead (Lanczos every 100 steps).
- **Total budget:** ~50-60 compute-hours, feasible on single machine.

### Timeline:
1. **Pilot:** 8 hours.
2. **Analysis & decision:** 2 hours.
3. **Confirmatory (if proceed):** 12 hours (parallelized).
4. **Controls & post-analysis:** 4 hours.
5. **Total:** ~24 hours wall-clock (within M-EXT4 budget of 24 hours cumulative).

---

## 11. Pre-Commitment: Seal & Hash

### Sealed elements (before pilot):
- Confirmatory seed values: 20 random seeds for (θ_hot, θ_cold, S_data).
- Seed generation: `numpy.random.SeedSequence(entropy=0xDEADBEEF_MPEMBA_M_EXT4)` (fixed entropy for reproducibility, publicly declared).
- Seeds stored in `SEALED_HOLDOUT.json`.
- SHA256 hash of sealed file recorded here:

**Sealed holdout hash (computed):**
```
SHA256(SEALED_HOLDOUT.json) = 050a83fb221e446a0651474ccb9bad05b4d683d8643e84ca0ab02bffe35a0e21
```

### Unsealing rule:
- Unseal ONLY after pilot decision (proceed/abandon).
- If proceed, use all 20 seeds in order (no selection).
- Any deviation from sealed seeds → INTEGRITY_VIOLATION → terminal.

---

## 12. Reporting & Transparency

### Deliverables:
1. **PREREG.md** (this document) — locked before pilot.
2. **PILOT_RESULTS.md** — pilot outcomes, decision log.
3. **CONFIRMATORY_RESULTS.md** — sealed confirmatory outcomes.
4. **COUNTEREVIDENCE.md** — null/negative findings, failures, anomalies.
5. **DECISION.md** — final terminal verdict with evidence summary.
6. **REPRODUCIBILITY_PACK.md** — code, seeds, data splits, instructions.

### Transparency commitments:
- Report **all** pilot seed outcomes (no cherry-picking).
- Report **all** confirmatory seed outcomes (including excluded pairs, with reasons).
- Report **all** competing-explanation control results (even if favorable to Mpemba).
- Report negative control outcomes (C4) even if they fail to support curvature mechanism.
- If effect is weak/borderline, report INCONCLUSIVE (not SUPPORTED).

---

## 13. Limitations (Pre-Declared)

1. **Small-scale setting:** 2-layer MLP on MNIST ≠ large-scale LLM (Liu&Hu setting). Effect may not scale.
2. **Fixed LR:** No WSD schedule (unlike Liu&Hu). Effect may be LR-schedule-dependent.
3. **Isotropic perturbation:** θ_hot/cold sampled from isotropic Gaussian (ignores Fisher geometry). True Fisher-informed sampling infeasible.
4. **Single target θ*:** Reference run is one sample. "Typical late regime" not ensemble-averaged.
5. **Parameter-space metric:** Even V1 (KL) is not pure Fisher-Rao geodesic (infeasible for DNNs).
6. **No mechanism proof:** Even if SUPPORTED, we don't prove *why* (Liu&Hu's slow-mode amplitude a₂(η) not directly computed here).

---

**END OF PREREGISTRATION**

**Status:** `LOCKED` after this commit.  
**Next:** Pilot experiment (Phase F).
