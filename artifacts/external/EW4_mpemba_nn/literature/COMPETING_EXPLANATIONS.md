# COMPETING EXPLANATIONS — M-EXT4 Mpemba Hypothesis

**Status:** `DRAFT`  
**Exam:** `M-EXT4-MPEMBA`  
**Date:** 2026-10-01  
**Purpose:** Enumerate alternative explanations for observed "hot overtakes cold" crossing, design controls to rule them out

---

## 0. Core Principle

**Mpemba effect claim:** Hot state (farther from target) reaches target faster due to **intrinsic relaxation dynamics** tied to loss-landscape geometry (Fisher curvature, slow-mode amplitude, etc.).

**Competing claim:** Observed crossing is **artifact** of:
- Experimental setup (batch order, random seed, optimizer quirks)
- Trivial mechanism (different initial loss → different gradient magnitudes)
- Overfitting / memorization (train-test mismatch)
- Coordinate system choice (reparametrization-dependent distance)

**Success criterion:** Mpemba claim holds **only if** competing explanations are ruled out via pre-planned controls.

---

## 1. Competing Explanation C1: Batch Order Effect

### Mechanism:
Hot initialization θ_hot happens to align better with early batch gradients → gets early "lucky breaks" → builds lead that persists even after cold catches up in later batches.

### Testable prediction:
If C1 is true, crossing should **disappear** or **flip** when batch order changes.

### Control:
```
Repeat experiment with K=5 different batch shuffle seeds.
For each seed, measure τ_hot and τ_cold.
Count n_wins = number of seeds where τ_hot < τ_cold.
```

### Decision rule:
- **Mpemba supported:** n_wins ≥ 4/5 (robust to batch order).
- **C1 supported (Mpemba rejected):** n_wins ≤ 1/5 (effect is batch-order artifact).
- **Inconclusive:** n_wins = 2 or 3 (weak effect, batch-order sensitive).

### Prereg commitment:
Pre-specify K=5 for pilot, K=20 for confirmatory (sealed). Require ≥ 14/20 wins for SUPPORTED verdict.

---

## 2. Competing Explanation C2: Random Seed Luck

### Mechanism:
θ_hot seed happens to be "lucky" (lands in basin with favorable geometry or close to easy descent path), θ_cold seed "unlucky" (lands on plateau or near saddle).

### Testable prediction:
If C2 is true, crossing should **not replicate** across multiple (hot, cold) seed pairs.

### Control:
```
Generate N=20 independent pairs (θ_hot^i, θ_cold^i) for i=1..20.
Each pair uses independent random seeds for sampling from N(θ*, σ^2 I).
For each pair, measure τ_hot^i, τ_cold^i.
Count n_wins = number of pairs where τ_hot^i < τ_cold^i.
```

### Decision rule:
- **Mpemba supported:** n_wins ≥ 14/20 (p < 0.05 under H0: equal probability, binomial test).
- **C2 supported (Mpemba rejected):** n_wins ~ 10/20 (no systematic advantage).

### Prereg commitment:
Use N=20 pairs in confirmatory. Pre-specify α=0.05 threshold (≥14 wins required).

---

## 3. Competing Explanation C3: Optimizer Momentum Artifact

### Mechanism:
If using SGD+momentum or Adam:
- Hot trajectory accumulates different momentum/2nd-moment estimates than cold.
- Momentum terms couple to current gradient → even with same batches, optimizer acts differently.
- Crossing may be momentum interaction, not intrinsic landscape dynamics.

### Testable prediction:
If C3 is true, crossing should **disappear** when using vanilla SGD (no momentum).

### Control:
```
Run experiment with two optimizer settings:
1. Vanilla SGD (no momentum).
2. SGD+momentum (momentum=0.9) or Adam.

Compare:
- Does crossing occur in vanilla SGD? (Mpemba test)
- Does crossing occur in SGD+momentum? (C3 test)
```

### Decision rule:
- **Mpemba supported:** Crossing in vanilla SGD (intrinsic effect, not momentum-dependent).
- **C3 supported (Mpemba rejected):** Crossing only in SGD+momentum, absent in vanilla SGD.
- **Ambiguous:** Crossing in both (Mpemba may exist but is enhanced by momentum).

### Prereg commitment:
**Primary test uses vanilla SGD** (no momentum). If crossing found, optionally test Adam as exploratory check (not part of primary endpoint).

---

## 4. Competing Explanation C4: Initial Loss Difference (Trivial Mechanism)

### Mechanism:
Hot initialization has higher initial loss L(θ_hot(0)) > L(θ_cold(0)).
Higher loss → larger gradients (if loss landscape is approximately quadratic: ||∇L|| ~ √(L - L*)).
Larger gradients → faster descent initially → hot catches up and overtakes cold.
This is **not** Mpemba effect (no geometric anomaly, just larger force).

### Testable prediction:
If C4 is true, crossing should **also occur** when hot/cold have same initial loss but different curvature is controlled away (negative control).

### Control (Negative Control):
```
Construct θ_hot_trivial and θ_cold_trivial:
- Perturb θ* along **same low-curvature eigendirection** v (e.g., smallest Hessian eigenvector).
- θ_hot_trivial = θ* + α_hot * v
- θ_cold_trivial = θ* + α_cold * v
- Choose α_hot, α_cold such that:
    L(θ_hot_trivial) ≈ L(θ_hot)  (match initial loss)
    L(θ_cold_trivial) ≈ L(θ_cold)

Train θ_hot_trivial and θ_cold_trivial with same protocol.
Check: Does crossing occur?
```

### Decision rule:
- **Mpemba supported (C4 rejected):** Crossing in (θ_hot, θ_cold) but NOT in (θ_hot_trivial, θ_cold_trivial) → curvature difference matters, not just loss difference.
- **C4 supported (Mpemba rejected):** Crossing in both → initial loss difference sufficient, no geometric effect.

### Prereg commitment:
Include negative control in confirmatory phase (at least 5 seed pairs). Pre-specify that Mpemba claim requires crossing to fail in negative control for ≥3/5 seeds.

---

## 5. Competing Explanation C5: Overfitting Artifact (Train-Test Mismatch)

### Mechanism:
Hot trajectory overfits faster (high-variance init → memorizes training data quickly).
Cold trajectory generalizes better (low-variance init → learns robust features).
Crossing observed in **train loss** but **test loss** crosses in opposite direction (cold overtakes hot on test).

### Testable prediction:
If C5 is true, train and test crossings should be **opposite**.

### Control:
```
Monitor both:
- D_train(θ(t), θ*) using training set
- D_test(θ(t), θ*) using held-out test set

Check crossing for both:
- Train crossing: t_train_cross where D_hot_train(t) < D_cold_train(t)
- Test crossing: t_test_cross where D_hot_test(t) < D_cold_test(t)

Compare: Do both occur? Do they agree in direction?
```

### Decision rule:
- **Mpemba supported:** Train and test crossings **both occur** and **agree** (hot faster in both train and test).
- **C5 supported (Mpemba rejected):** Train crossing occurs but test crossing **absent** or **opposite** → overfitting artifact.

### Prereg commitment:
**Primary endpoint:** Test-set crossing (or test-loss crossing).
If train crossing present but test crossing absent → declare **REJECTED** (overfitting artifact, not Mpemba).

---

## 6. Competing Explanation C6: Adaptive Learning Rate Interaction

### Mechanism:
If using learning rate schedule (e.g., ReduceLROnPlateau):
- Hot and cold may trigger LR reductions at different times.
- Different effective LR profiles → different convergence speeds.
- Crossing is LR-schedule artifact, not intrinsic dynamics.

### Testable prediction:
If C6 is true, crossing should **disappear** or **change** with fixed LR (no schedule).

### Control:
```
Use fixed LR (no warmup, no decay, no adaptive schedule).
```

### Decision rule:
- **Mpemba supported:** Crossing occurs with fixed LR → not LR-schedule artifact.
- **C6 supported (Mpemba rejected):** Crossing only with adaptive LR, absent with fixed LR.

### Prereg commitment:
**Use fixed LR η=0.01 throughout** (no schedule). This design choice rules out C6 by construction.

---

## 7. Competing Explanation C7: Coordinate Artifact (Reparametrization Dependence)

### Mechanism (for V2 formulation with L2 distance):
Distance D(θ, θ*) = ||θ - θ*||_2 is not reparametrization-invariant.
Example: Scale layer 1 weights by factor c, layer 2 weights by 1/c → network output unchanged, but L2 distance changes.
Observed crossing may flip under reparametrization → not intrinsic effect, but coordinate system artifact.

### Testable prediction:
If C7 is true, crossing should **flip** or **disappear** under reparametrization.

### Control (for V2 only):
```
After finding crossing with original parametrization θ:
1. Define reparametrization R: multiply layer 1 weights by c=2, layer 2 weights by 0.5.
2. Transform: θ' = R(θ), θ_hot' = R(θ_hot), θ_cold' = R(θ_cold).
3. Network output unchanged: f(x; θ') = f(x; θ) for all x.
4. Recompute distances D'(θ_hot'(t), θ*') and D'(θ_cold'(t), θ*').
5. Check: Does crossing still occur?
```

### Decision rule:
- **Mpemba supported (C7 rejected):** Crossing persists under reparametrization (robust).
- **C7 supported (Mpemba ILL_POSED):** Crossing flips or disappears → coordinate artifact.

### Prereg commitment:
- **V1 (KL-based distance):** Immune to C7 (KL is reparametrization-invariant) → skip this control.
- **V2 (L2 distance):** Include reparametrization check. If crossing flips → terminal **ILL_POSED** for V2, must retry with V1.

---

## 8. Competing Explanation C8: Edge-of-Stability Interaction

### Mechanism:
Hot init may place network in different sharpness regime than cold.
Example: Sharpness λ_max_hot(0) > 2/η → hot trajectory enters Edge-of-Stability (EoS) dynamics (non-monotonic loss).
Cold trajectory stays below 2/η → monotonic descent.
EoS dynamics may cause hot to explore more → accidentally find better descent path → overtake cold.
This is **not Mpemba** (EoS is known phenomenon, not relaxation-mode amplitude effect).

### Testable prediction:
If C8 is true, crossing should correlate with sharpness crossing (λ_max_hot crosses below λ_max_cold before distance crossing).

### Control:
```
Monitor sharpness λ_max(t) for hot and cold:
- Approximate via power iteration or Lanczos (sample every 100 steps).
- Check:
    1. Does λ_max_hot(0) > λ_max_cold(0)?
    2. Does λ_max_hot(t_sharp_cross) < λ_max_cold(t_sharp_cross) for some t_sharp_cross < t_dist_cross?
    3. Does λ_max_hot(t) hover near 2/η (EoS signature)?
```

### Decision rule:
- **Mpemba supported (C8 rejected):** Distance crossing occurs **without** sharpness crossing or EoS signature → intrinsic effect.
- **C8 supported (Mpemba INCONCLUSIVE):** Distance crossing coincides with EoS entry → ambiguous (could be EoS-enabled Mpemba or EoS artifact).

### Prereg commitment:
Include sharpness monitoring in confirmatory (every 100 steps, Lanczos approximation).
If λ_max_hot ~ 2/η detected → flag as EoS interaction, require additional analysis to disentangle.

---

## 9. Competing Explanation C9: Loss Landscape Multi-Modality

### Mechanism:
Hot and cold land in **different basins** of loss landscape (not same attractor).
They converge to different local minima θ*_hot ≠ θ*_cold.
Apparent "crossing" is artifact: they're heading to different targets, not same target.

### Testable prediction:
If C9 is true, final losses L(θ_hot(T)) and L(θ_cold(T)) should **differ significantly**.

### Control:
```
Train hot and cold to convergence (T=10,000 steps or until plateau).
Check:
- Final loss: |L(θ_hot(T)) - L(θ_cold(T))| < δ (e.g., δ=0.01)?
- Final distance to θ*: D(θ_hot(T), θ*) and D(θ_cold(T), θ*) both small?

If final losses differ → different basins → exclude seed pair from analysis.
```

### Decision rule:
- **Mpemba testable:** Final losses agree (same basin) → proceed with crossing analysis.
- **C9 present (seed pair excluded):** Final losses differ → different basins → cannot test Mpemba for this pair.

### Prereg commitment:
Pre-specify exclusion criterion: exclude pairs where |L_hot(T) - L_cold(T)| > 0.05.
If >50% of seed pairs excluded → loss landscape too multi-modal → terminal **ILL_POSED** (cannot define common target R*).

---

## 10. Competing Explanation C10: Implicit Regularization Difference

### Mechanism:
SGD has implicit regularization (Ash&Adams 2020, DASH 2024):
- High-variance init → SGD penalizes complexity differently than low-variance init.
- Hot and cold may converge to different "effective" minima even if same basin.
- Crossing is implicit-reg artifact, not Mpemba.

### Testable prediction:
If C10 is true, crossing should **change** when adding explicit L2 regularization (which swamps implicit reg).

### Control:
```
Repeat experiment with explicit L2 regularization:
Loss_reg(θ) = Loss(θ) + λ ||θ - θ*||_2^2, λ=0.01.

Compare:
- Crossing in unregularized setting?
- Crossing in L2-regularized setting?
```

### Decision rule:
- **Mpemba supported (C10 rejected):** Crossing persists with L2 regularization → not implicit-reg artifact.
- **C10 supported (Mpemba INCONCLUSIVE):** Crossing disappears with L2 reg → implicit regularization may be mechanism (related but distinct from Mpemba).

### Prereg commitment:
Primary test: unregularized.
Exploratory: L2-regularized (not part of primary endpoint, but useful for interpretation).

---

## 11. Summary Table: Controls and Falsification

| Competing Explanation | Control Design | Mpemba Supported If | Mpemba Rejected If | Prereg Status |
|-----------------------|----------------|---------------------|---------------------|---------------|
| **C1: Batch order** | 20 batch shuffles | τ_hot < τ_cold in ≥14/20 | ≤6/20 | **Primary control** |
| **C2: Random seed luck** | 20 (hot, cold) pairs | ≥14/20 pairs win | ~10/20 | **Primary control** |
| **C3: Momentum artifact** | Vanilla SGD (no momentum) | Crossing in vanilla SGD | Crossing only with momentum | **Design choice (vanilla SGD)** |
| **C4: Initial loss (trivial)** | Negative control (same curvature) | Crossing fails in negative | Crossing in both | **Secondary control (5 pairs)** |
| **C5: Overfitting** | Train + test crossing | Both agree | Train≠test | **Primary endpoint (test crossing)** |
| **C6: Adaptive LR** | Fixed LR (no schedule) | Crossing with fixed LR | N/A | **Design choice (fixed LR)** |
| **C7: Coordinate artifact** | Reparametrization check (V2) | Robust to reparam | Flips under reparam | **V2 only** |
| **C8: Edge-of-Stability** | Sharpness monitoring | No EoS signature | λ_max ~ 2/η | **Diagnostic (confirmatory)** |
| **C9: Multi-modality** | Final loss agreement | |L_hot - L_cold| < 0.05 | >50% pairs excluded | **Exclusion criterion** |
| **C10: Implicit reg** | Explicit L2 reg (exploratory) | Robust to L2 | Disappears with L2 | **Exploratory (not primary)** |

---

## 12. Integrated Decision Logic

```
Run confirmatory experiment (20 seed pairs, 20 batch shuffles):

1. For each seed pair i=1..20:
   a. Check multi-modality (C9): |L_hot^i(T) - L_cold^i(T)| < 0.05?
      → If NO: exclude pair.
   b. Check crossing on TEST set (C5): τ_hot_test^i < τ_cold_test^i?
      → If YES: record win.
   c. Check batch-order robustness (C1): crossing holds for ≥16/20 batch shuffles?
      → If NO: exclude pair.

2. Count n_valid_pairs = pairs not excluded.
   If n_valid_pairs < 10 → terminal ILL_POSED (loss landscape too fragmented).

3. Count n_wins = valid pairs where τ_hot_test < τ_cold_test.
   Binomial test: n_wins >= 0.7 * n_valid_pairs (p < 0.05)?
   → If YES: Mpemba SUPPORTED (on test set, batch-robust, multi-modal-filtered).
   → If NO: Mpemba REJECTED.

4. Run negative control (C4) on 5 randomly selected valid pairs:
   Does crossing fail in ≥3/5 negative-control pairs?
   → If YES: Mpemba mechanism is curvature-related (not trivial loss difference).
   → If NO: Mpemba INCONCLUSIVE (mechanism unclear).

5. Check sharpness (C8) for all valid pairs:
   Do ≥50% of winning pairs show λ_max_hot ~ 2/η (EoS signature)?
   → If YES: Flag EoS interaction (Mpemba may be EoS-assisted, report limitation).
   → If NO: Mpemba is EoS-independent.

6. For V2 (L2 distance), run reparametrization check (C7) on 5 pairs:
   Does crossing persist under reparametrization for ≥4/5?
   → If YES: V2 result robust.
   → If NO: V2 result is coordinate artifact → terminal ILL_POSED for V2, revert to V1.

FINAL VERDICT:
- SUPPORTED_WITHIN_SCOPE: n_wins ≥ 0.7 * n_valid_pairs, negative control passes, no C7 failure.
- REJECTED: n_wins < 0.7 * n_valid_pairs OR negative control fails.
- ILL_POSED: n_valid_pairs < 10 OR C7 failure (V2) and V1 infeasible.
- INCONCLUSIVE: Edge cases (weak effect, EoS-dominated, etc.).
```

---

**END OF COMPETING_EXPLANATIONS — Phase D complete**

**Next:** PREREG.md (Phase E — preregistration document before pilot)
