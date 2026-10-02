# FORMALIZATION — M-EXT4 Mpemba Hypothesis

**Status:** `DRAFT`  
**Exam:** `M-EXT4-MPEMBA`  
**Date:** 2026-10-01  
**Purpose:** Rigorous mathematical formulation, identification of ill-defined terms, operational alternatives, scope narrowing

---

## 0. Executive Summary

**Mathematical audit verdict:** User hypothesis contains **multiple ill-defined or conflicting terms** that prevent direct empirical test without clarification. Below we enumerate problems, propose operational alternatives, and narrow scope to a testable claim.

**Scope narrowing required:** Original claim overlaps substantially with Liu&Hu 2025. To avoid `NOT_NOVEL_IN_CLAIMED_FORM`, we restrict to:
- **Initialization-based construction** (not LR-schedule-based)
- **Fixed LR** (not WSD schedule)
- **Small controlled models** (2-layer MLP, MNIST/CIFAR-10 subset)
- **Preregistered falsification test** (competing explanations ruled out)

**Formalization outcome:** We provide two versions:
1. **V1 (Strict):** Requires Fisher-Rao distance (computationally expensive, may be infeasible).
2. **V2 (Relaxed):** Uses parameter-space L2 + sharpness-aware target definition (testable, but weaker interpretation).

If V1 is infeasible and V2 crosses turn out to be coordinate artifacts or optimizer quirks → terminal `ILL_POSED` or `REJECTED`.

---

## 1. Problems in Original Hypothesis (SOURCE_HYPOTHESIS.md)

### P1: "Общий конечный режим обучения R*" undefined

**User text:**
> существует ... общий «конечный режим обучения» \(\mathcal{R}_*\) (окрестность типичного позднего режима / выбранного target regime)

**Problems:**
1. **"Типичный поздний режим"** — typical over what ensemble? Multiple runs? Different seeds? Different initializations? Different batch orders?
2. **"Окрестность"** — size ε of ball/ellipsoid? In which metric?
3. **"Выбранного target regime"** — chosen by whom? Based on what criterion? Post-hoc or pre-specified?

**Consequences:**
- Without operational definition, cannot compute D(θ, R*).
- Experimenter could choose R* post-hoc to maximize Mpemba appearance (p-hacking).

**Operational alternatives:**

**Alt 1.1 (Ensemble mean of late checkpoints):**
```
Train K=20 independent runs (random seeds) for T_total steps.
Collect checkpoints from t ∈ [T_late_start, T_total] where T_late_start = 0.8 * T_total.
Define θ* = mean of all late checkpoints (parameter-space average).
Define R* = ball of radius ε around θ* in chosen metric.
```
- **Pro:** Operational, reproducible.
- **Con:** Mean in parameter space may not correspond to meaningful network (mode collapse if θ's are in different basins).

**Alt 1.2 (Consensus minimum):**
```
Train K runs to convergence (train loss < threshold).
Identify all distinct minima (cluster final θ's by loss-landscape connectivity).
If ≥ 80% of runs converge to same basin, define θ* = centroid of that basin.
Otherwise declare R* ill-defined (multi-modal landscape).
```
- **Pro:** Respects loss landscape geometry.
- **Con:** Clustering requires expensive loss-landscape probes (mode connectivity algorithms).

**Alt 1.3 (Fixed reference from single run):**
```
Train one reference run to convergence → θ_ref.
Define θ* = θ_ref.
Define R* = {θ : D(θ, θ*) < ε}.
```
- **Pro:** Simple, no averaging.
- **Con:** θ* is single sample, not "typical regime" — effect may be specific to this θ*.

**Recommendation:** Use Alt 1.3 for pilot, Alt 1.2 for confirmatory (if computationally feasible). Pre-specify in prereg.

---

### P2: Distance metric D(θ, R*) not specified

**User text:**
> по заранее выбранной метрике расстояния \(D\)

**Problems:**
1. Raw Euclidean L2 distance is **reparametrization-dependent** (Kim et al. 2022 Fisher-SAM: L2(θ - θ') does not reflect distributional distance).
2. User mentions "Fisher–Rao–подобная геометрия" but does not commit.
3. Fisher-Rao distance requires FIM^{-1}, which is often singular in DNNs (Karakida 2019).

**Operational alternatives:**

**Alt 2.1 (Parameter-space L2):**
```
D(θ, θ*) = ||θ - θ*||_2
```
- **Pro:** Computable, deterministic.
- **Con:** Reparametrization-dependent; two networks with same output distribution can have vastly different L2 distances.
- **Risk:** Observed "crossing" could be artifact of coordinate choice (e.g., rescaling one layer weights).

**Alt 2.2 (Fisher-Rao / KL-based):**
```
D_KL(θ, θ*) = E_{x ~ data} [ KL( p(y|x, θ*) || p(y|x, θ) ) ]
or symmetrized version: (KL(θ* || θ) + KL(θ || θ*)) / 2
```
- **Pro:** Reparametrization-invariant, measures distributional distance.
- **Con:** Expensive to compute (requires forward pass on full dataset for each D evaluation). Monte-Carlo estimate needed.
- **Con:** For regression with Gaussian likelihood, reduces to MSE-based distance (loses Fisher geometry flavor).
- **Con:** For classification with softmax, may be dominated by high-confidence examples (need to check calibration).

**Alt 2.3 (Fisher-Rao geodesic distance — infeasible):**
```
Compute geodesic distance on statistical manifold with Fisher metric.
```
- **Pro:** True intrinsic geometry.
- **Con:** Requires FIM^{-1} at every step along geodesic → computationally infeasible for DNNs (FIM often rank-deficient).

**Alt 2.4 (Trace-based Fisher proxy):**
```
D_F(θ, θ*) = sqrt( E_x [ ||∇_θ log p(y|x,θ) - ∇_θ log p(y|x,θ*)||_2^2 ] )
```
- **Pro:** Related to Fisher information, avoids inversion.
- **Con:** Still expensive (gradient computations).

**Alt 2.5 (Loss-based proxy):**
```
D_loss(θ, θ*) = | L(θ) - L(θ*) |
where L(θ) = E_{(x,y) ~ data} [ loss(f(x; θ), y) ]
```
- **Pro:** Cheap, directly interpretable.
- **Con:** Not a metric (violates triangle inequality, non-symmetric in general for non-convex loss).
- **Con:** Two networks in different basins can have same loss but different geometry.

**Recommendation:**
- **Pilot:** Use Alt 2.1 (L2) + Alt 2.5 (loss) to check if any crossing exists.
- **Confirmatory:** Use Alt 2.2 (KL-based, Monte-Carlo estimate on holdout set) if pilot shows crossing.
- **Pre-register:** State metric in prereg; do NOT switch metric post-hoc to "rescue" effect.

---

### P3: "Характерный масштаб H_e" conflates multiple scales

**User text:**
> Оценить характерный масштаб \(H_e\) (например, связанный с типичной инициализацией / energy / Hessian–Fisher scale)

**Problems:**
1. **Typical init scale:** e.g., Xavier σ_Xavier = sqrt(2 / (fan_in + fan_out)) — depends on layer.
2. **Energy scale:** From loss? Which loss value? Initial? Final? Range?
3. **Hessian scale:** λ_max of Hessian — varies during training (Edge of Stability: grows to ~2/η).
4. **Fisher scale:** λ_max of FIM — also varies, can explode early (Catastrophic Fisher Explosion).

**These scales differ by orders of magnitude.**

**User proposed construction:**
> - σ_hot = 2 × H_e
> - σ_cold = 0.3 × H_e

**Ambiguity:** If H_e is init scale, σ_hot = 2 × σ_Xavier makes sense. If H_e is Hessian eigenvalue, σ_hot = 2 × λ_max is dimensionally wrong (λ_max has units of curvature, not parameter std).

**Operational alternatives:**

**Alt 3.1 (Initialization-scale based):**
```
For each layer l, compute typical init std σ_l (e.g., Kaiming or Xavier).
Define H_e = mean(σ_l) across layers (or geometric mean).
Hot init: sample θ_hot ~ N(θ*, (α_hot * H_e)^2 * I) with α_hot = 2.
Cold init: sample θ_cold ~ N(θ*, (α_cold * H_e)^2 * I) with α_cold = 0.3.
```
- **Pro:** Dimensionally consistent, interpretable as "re-initialization around θ* with different temperatures".
- **Con:** Ignores Fisher geometry (isotropic Gaussian in parameter space).

**Alt 3.2 (Hessian-informed scale):**
```
Compute Hessian at θ* (or approximate with Hutchinson trace estimator).
Extract λ_max (largest eigenvalue).
Define perturbation scale proportional to 1/sqrt(λ_max) (natural scale for quadratic bowl).
Hot init: θ_hot = θ* + ε_hot * v_random, where ||ε_hot|| = α_hot / sqrt(λ_max).
Cold init: θ_cold = θ* + ε_cold * v_random, where ||ε_cold|| = α_cold / sqrt(λ_max).
```
- **Pro:** Respects local curvature.
- **Con:** Hessian computation expensive (even approximation requires multiple forward/backward passes).

**Alt 3.3 (Fisher-informed scale — infeasible):**
```
Compute FIM at θ*, extract λ_max(FIM).
Sample from Gaussian with covariance ~ FIM^{-1}.
```
- **Pro:** True Fisher geometry.
- **Con:** FIM inversion infeasible for DNNs.

**Alt 3.4 (Loss-range based):**
```
Compute loss at θ*: L*.
Compute loss at random init θ_rand: L_rand.
Define energy scale ΔL = L_rand - L*.
Perturb θ* along random direction until loss increases by α * ΔL.
Hot: α_hot = 0.5 (halfway back to random init loss).
Cold: α_cold = 0.05 (small perturbation).
```
- **Pro:** Loss-based, interpretable.
- **Con:** Perturbation magnitude depends on loss landscape shape (could land outside basin).

**Recommendation:** Use Alt 3.1 (init-scale based) for simplicity in pilot. Pre-specify α_hot and α_cold (e.g., α_hot = 2, α_cold = 0.3). If effect depends critically on exact α values → weak effect, fragile.

---

### P4: "Одинаковая последующая динамика" harder than it appears

**User text:**
> При **одинаковой** последующей динамике (тот же optimizer, те же данные/батчи, тот же noise process / seed pairing где применимо)

**Problems:**
1. **Random seed coupling:** Hot and cold must see **identical** minibatch order and **identical** SGD noise ξ(t). Naive approach: different random seeds for hot/cold → different batch shuffle → confounded.
2. **Optimizer state:** Momentum-based optimizers (SGD+momentum, Adam) accumulate state (velocity, 2nd moment estimates). If hot and cold have different θ(t) trajectories, their optimizer states diverge → optimizer acts differently even with same batches.
3. **Batch normalization / Dropout:** If network has BN or Dropout, running statistics and dropout masks introduce additional stochasticity. Must ensure these are also coupled across hot/cold.

**Operational alternatives:**

**Alt 4.1 (Shared batch order, independent optimizer state):**
```
Fix batch shuffle seed = S_data.
Train hot and cold with same batch order.
Use independent random seeds for weight init (hot vs cold).
Allow optimizer state to evolve independently per trajectory.
```
- **Pro:** Simple to implement.
- **Con:** Optimizer state coupling breaks "identical dynamics" — momentum hot ≠ momentum cold.

**Alt 4.2 (Coupled SGD noise — difficult):**
```
Use vanilla SGD (no momentum).
Fix batch order seed.
For noise in parameter updates (if added explicitly, e.g., Langevin dynamics), use same noise seed for hot and cold at each step t.
```
- **Pro:** Truly identical dynamics post-init.
- **Con:** Requires deterministic batch sampling and no momentum (momentum breaks coupling).
- **Con:** Vanilla SGD may not exhibit effect if effect relies on momentum/Adam adaptation.

**Alt 4.3 (Replay buffer approach):**
```
Pre-record all batches and noise realizations for T steps.
Replay same sequence for hot and cold.
```
- **Pro:** Guaranteed identical external forcing.
- **Con:** Still doesn't fix optimizer state coupling for Adam/momentum.

**Recommendation:**
- **Pilot:** Use Alt 4.1 (shared batch order, vanilla SGD or SGD+momentum with independent state).
- **Confirmatory:** If effect found, retest with Alt 4.2 (vanilla SGD, no momentum) to rule out optimizer-state artifacts.
- **Pre-register:** Specify optimizer (vanilla SGD preferred for clean test).

---

### P5: "Crossing" definition ambiguous

**User text:**
> Наблюдается **crossing** траекторий по \(D(\theta(t),\mathcal{R}_*)\) (или по согласованной relaxation coordinate)

**Problems:**
1. Crossing in D(θ(t), θ*) ≠ crossing in loss L(θ(t)) ≠ crossing in test error.
2. Non-monotonic loss common in NN training (Edge of Stability, grokking) — not all crossings are Mpemba effect.
3. "Согласованная relaxation coordinate" not defined — projection onto slow eigenmode u_2? (Requires computing u_2, expensive.)

**Operational definition:**

**Def 5.1 (Distance crossing):**
```
Let D_hot(t) = D(θ_hot(t), θ*).
Let D_cold(t) = D(θ_cold(t), θ*).
Define crossing time t_cross = min { t : D_hot(0) > D_cold(0) AND D_hot(t) < D_cold(t) }.
Mpemba effect present if t_cross < T_max (some reasonable horizon).
```
- **Pro:** Clear operational definition.
- **Con:** Single crossing may be noise fluctuation; need sustained crossing (D_hot < D_cold for t ∈ [t_cross, t_cross + Δt]).

**Def 5.2 (First-passage time):**
```
Define target set R* = {θ : D(θ, θ*) < ε}.
Define τ_hot = min { t : θ_hot(t) ∈ R* }.
Define τ_cold = min { t : θ_cold(t) ∈ R* }.
Mpemba effect present if τ_hot < τ_cold.
```
- **Pro:** Matches Liu&Hu formalism exactly.
- **Con:** Requires choosing ε; effect may be sensitive to ε.

**Recommendation:** Use both Def 5.1 and Def 5.2 in confirmatory. Require both to hold for Mpemba claim.

---

## 2. Reformulated Hypothesis (Operational Version)

### V1: Strict Fisher-Geometric Version (Hard)

**Setting:**
- Architecture: 2-layer MLP, width w=128, ReLU activation
- Dataset: MNIST (or CIFAR-10 if MLP insufficient)
- Loss: Cross-entropy
- Optimizer: Vanilla SGD (no momentum), fixed LR η

**Procedure:**
1. Train reference run to convergence → θ_ref (train loss < 0.01).
2. Define θ* = θ_ref.
3. Compute KL-based distance: D(θ, θ*) = E_x [ KL( p(y|x,θ*) || p(y|x,θ) ) ] (Monte-Carlo estimate on held-out calibration set).
4. Define hot/cold init:
   - θ_hot ~ N(θ*, σ_hot^2 I), σ_hot = 2 * σ_Xavier_mean
   - θ_cold ~ N(θ*, σ_cold^2 I), σ_cold = 0.3 * σ_Xavier_mean
5. Check initial condition: D(θ_hot(0), θ*) > D(θ_cold(0), θ*).
6. Train both with **same batch order** (fixed seed S_data), vanilla SGD, fixed LR.
7. Monitor D_hot(t), D_cold(t) every k steps (k=10).
8. Define target set R* = {θ : D(θ, θ*) < ε} where ε = 0.1 * D(θ_rand, θ*) (10% of random-init distance).
9. Record first-passage times τ_hot, τ_cold.

**Mpemba criterion:**
- **Primary:** τ_hot < τ_cold (hot reaches target first).
- **Secondary:** Crossing observed: ∃ t_cross such that D_hot(t_cross) < D_cold(t_cross) and crossing is sustained (D_hot < D_cold for t ∈ [t_cross, t_cross + 50 steps]).

**Competing explanations to rule out:**
- Batch order effect: Repeat with 5 different batch shuffle seeds → Mpemba should hold for ≥ 4/5.
- Random seed effect: Repeat with 10 random seeds for (θ_hot, θ_cold) pairs → τ_hot < τ_cold for ≥ 7/10 pairs.
- Loss vs distance: Check if crossing holds for loss L(θ(t)) as well as D(θ(t), θ*).
- Generalization: Check test loss crossing (may go opposite direction).

**Falsification criteria:**
- NO crossing in ≥ 6/10 seeds → REJECTED.
- Crossing only in train loss, test loss crosses opposite → NOT Mpemba (overfitting artifact) → REJECTED.
- Crossing disappears when switching from L2 to KL distance → coordinate artifact → ILL_POSED.

---

### V2: Relaxed Parameter-Space Version (Easier, Weaker Interpretation)

Same as V1, but:
- Use D(θ, θ*) = ||θ - θ*||_2 (L2 distance in parameter space).
- Acknowledge reparametrization-dependence in limitations.

**Falsification addendum for V2:**
- If crossing found, must verify it's not coordinate artifact: re-run with network reparametrization (e.g., scale layer 1 weights by 2, scale layer 2 by 0.5 to keep output unchanged). If crossing flips → coordinate artifact → ILL_POSED.

---

## 3. Scope Restriction to Preserve Novelty (vs Liu&Hu 2025)

Liu&Hu claim Mpemba effect in **LLM training with WSD (warmup-stable-decay) LR schedule**, where:
- Hot = high plateau LR (e.g., η_plateau = 1e-3)
- Cold = low plateau LR (e.g., η_plateau = 1e-4)
- Both decay to same final LR (e.g., η_final = 1e-5)

**Our narrowed claim:**
- **Initialization-based** (not LR-schedule-based)
- **Fixed LR** (no warmup, no decay)
- **Small controlled nets** (2-layer MLP, not LLM)
- **Preregistered falsification test**

**Novelty argument if V1 or V2 confirms Mpemba:**
- "Mpemba effect exists in NN training via initialization perturbation at fixed LR, independent of LR schedule, confirmed in preregistered test on small controlled architecture, ruling out competing explanations X, Y, Z."

**Novelty argument if V1/V2 REJECTS:**
- "Mpemba effect claimed by Liu&Hu (LR-schedule-based) does NOT generalize to initialization-based construction at fixed LR in small nets → effect may be specific to LR-schedule manipulation or large-scale valley-river landscapes."

Both outcomes are novel vs Liu&Hu (who did not test initialization-based construction and acknowledged lack of empirical validation).

---

## 4. Stronger Mechanism Claim (Fisher / Curvature)

**User text:**
> Эффект связан с **Fisher information / curvature geometry** loss landscape (а не сводится к тривиальному различию в начальном training loss).

**Operational test:**
1. **Negative control:** Create θ_hot_trivial and θ_cold_trivial such that:
   - L(θ_hot_trivial(0)) = L(θ_hot(0))
   - L(θ_cold_trivial(0)) = L(θ_cold(0))
   - BUT: θ_hot_trivial and θ_cold_trivial are chosen to have **same** curvature (e.g., both perturb θ* along same low-curvature direction, different magnitudes).
2. If Mpemba crossing observed for (θ_hot, θ_cold) but NOT for (θ_hot_trivial, θ_cold_trivial) → supports curvature mechanism.
3. If crossing observed for both → initial loss difference sufficient, Fisher geometry not necessary.

**Hessian / Fisher eigenspectrum check:**
1. Compute Hessian eigenspectrum at θ*, θ_hot(0), θ_cold(0) (or top-k eigenvalues via Lanczos).
2. Check: Does θ_hot(0) have higher λ_max (sharpness) than θ_cold(0)?
3. Track sharpness λ_max(t) for hot and cold during training.
4. If sharpness_hot(0) > sharpness_cold(0) and sharpness_hot crosses below sharpness_cold before distance crossing → consistent with Liu&Hu mechanism.

**Recommendation:** Include Hessian eigenvalue monitoring in confirmatory (even if expensive, sample every 100 steps). If no curvature difference between hot and cold → Fisher mechanism claim REJECTED.

---

## 5. Summary of Definitions for Prereg

### Fixed elements:
- **Architecture:** 2-layer MLP, width 128, ReLU
- **Dataset:** MNIST (or CIFAR-10 if needed)
- **Loss:** Cross-entropy
- **Optimizer:** Vanilla SGD, LR η = 0.01 (fixed, no decay)
- **Reference:** θ* from single converged run (train loss < 0.01)

### Hot/Cold construction:
- **H_e:** Mean of layer-wise Xavier init scales
- **σ_hot = 2 * H_e**, **σ_cold = 0.3 * H_e**
- **θ_hot ~ N(θ*, σ_hot^2 I)**, **θ_cold ~ N(θ*, σ_cold^2 I)**
- **Initial condition check:** D(θ_hot(0), θ*) > D(θ_cold(0), θ*) (if fails, resample)

### Distance metrics:
- **Primary (V1):** D_KL(θ, θ*) = E_x [KL(p(y|x,θ*) || p(y|x,θ))]
- **Secondary (V2):** D_L2(θ, θ*) = ||θ - θ*||_2

### Target set:
- **R* = {θ : D(θ, θ*) < ε}**, **ε = 0.1 * D(θ_rand, θ*)**

### Mpemba criteria:
1. **First-passage:** τ_hot < τ_cold
2. **Crossing:** ∃ t_cross < T_max : D_hot(t_cross) < D_cold(t_cross), sustained for ≥ 50 steps

### Sample size:
- **Pilot:** 5 random seeds
- **Confirmatory:** 20 random seeds (sealed)

### Falsification:
- **Reject if:** τ_hot < τ_cold in < 14/20 seeds (p < 0.05 binomial test under H0: p=0.5)
- **Reject if:** Train-loss crossing present but test-loss crossing absent (overfitting artifact)
- **ILL_POSED if:** Effect flips under reparametrization (for V2)

---

## 6. Open Questions / Residual Ambiguities

1. **Multi-modality:** If θ* is in one basin but random perturbations land in other basins, hot/cold may never reach R* (different attractors). → Check loss landscape connectivity first (pilot phase).

2. **Edge-of-Stability interaction:** If hot init triggers EoS dynamics (sharpness ~2/η) but cold does not, crossing may be EoS artifact, not Mpemba. → Monitor sharpness.

3. **Batch size:** Small batch → high noise, may wash out effect. Large batch → low noise, closer to GD. → Pilot with batch size sweep (32, 128, 512).

4. **Architecture dependence:** Effect may exist in linear models but not MLPs (or vice versa). → Include linear regression baseline in pilot.

5. **Temperature interpretation:** User calls high-variance init "hot" by analogy to thermodynamics. But SGD LR is the temperature in Langevin view (Liu&Hu). Mixing both (high-variance init + high LR) may confound. → Test (σ_hot, LR_low) vs (σ_cold, LR_high) as cross-check.

---

## 7. Decision Tree

```
Formalization complete → Prereg
  ↓
Pilot (5 seeds)
  ↓
  ├─ No crossing in any seed → REJECTED (skip confirmatory)
  ├─ Crossing in 1-2 seeds → Underpowered, inconclusive → need more seeds or stronger effect
  └─ Crossing in ≥ 3/5 seeds → Proceed to confirmatory
      ↓
Confirmatory (20 seeds, sealed)
  ↓
  ├─ τ_hot < τ_cold in ≥ 14/20 → SUPPORTED_WITHIN_SCOPE
  ├─ τ_hot < τ_cold in < 14/20 → REJECTED
  ├─ Train-test crossing mismatch → REJECTED (overfitting)
  ├─ Effect flips under reparametrization → ILL_POSED
  └─ Competing explanation not ruled out → INCONCLUSIVE
```

---

**END OF FORMALIZATION — Phase C complete**

**Next:** COMPETING_EXPLANATIONS.md (Phase D), then PREREG.md (Phase E)
