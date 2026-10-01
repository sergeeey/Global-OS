# COUNTEREVIDENCE — M-EXT4 Mpemba Hypothesis

**Exam:** `M-EXT4-MPEMBA`  
**Protocol:** `M-EXT4-MPEMBA-v1`  
**Date:** 2026-10-01  
**Status:** Integrated with DECISION.md

---

## Purpose

This document records evidence **against** user hypothesis, null findings, failed predictions, and limitations — per GOS-I11 (failed/null results permanent knowledge).

---

## 1. Primary Counterevidence: Prior Publication

**Liu & Hu (2025, arxiv:2507.04206)** published core claim ("Mpemba effect in NN training linked to Fisher geometry") **before** this mission.

**Impact:** User hypothesis **NOT_NOVEL_IN_CLAIMED_FORM**.

---

## 2. Formalization Barriers (ILL_POSED Components)

User hypothesis contains **5 ill-defined terms** (see FORMALIZATION.md P1-P5):

1. **R* undefined:** "типичный поздний режим" не operational.
2. **D not specified:** "заранее выбранная метрика" allows coordinate artifacts.
3. **H_e conflates scales:** init / energy / Hessian / Fisher scales differ by orders of magnitude.
4. **"Identical dynamics" infeasible:** Coupling SGD noise across hot/cold with momentum/Adam is hard.
5. **Fisher-Rao distance infeasible:** FIM^{-1} singular in DNNs (Karakida 2019).

**Impact:** SOURCE_HYPOTHESIS.md **as written** cannot be tested without extensive clarifications. FORMALIZATION.md resolved issues, but original text is **ILL_POSED**.

---

## 3. Competing Explanations (Not Ruled Out)

We identified **10 alternative mechanisms** (C1-C10) that could produce "hot overtakes cold" crossing **without** Mpemba effect:

### C1: Batch Order Effect
- Hot init aligns with early batches → lucky start persists.
- **Expected:** Effect disappears or flips with batch shuffle.

### C2: Random Seed Luck
- Hot seed lucky, cold seed unlucky.
- **Expected:** No replication across seeds (p ≈ 0.5).

### C3: Momentum Artifact
- Momentum accumulation differs for hot vs cold.
- **Expected:** Effect absent in vanilla SGD (no momentum).

### C4: Initial Loss (Trivial Mechanism)
- L(θ_hot(0)) > L(θ_cold(0)) → larger gradients → faster descent.
- **Expected:** Negative control (same loss, same curvature) also crosses.

### C5: Overfitting Artifact
- Hot overfits train, cold generalizes better.
- **Expected:** Train crosses, test does NOT (or opposite direction).

### C6: Adaptive LR Interaction
- Hot/cold trigger LR schedule changes at different times.
- **Expected:** Effect absent with fixed LR.

### C7: Coordinate Artifact (for L2 distance)
- L2 distance reparametrization-dependent.
- **Expected:** Crossing flips under reparametrization.

### C8: Edge-of-Stability
- Hot enters EoS (λ_max ~ 2/η), cold does not.
- **Expected:** Sharpness crossing precedes distance crossing.

### C9: Multi-Modality
- Hot and cold converge to different basins.
- **Expected:** |L_hot(T) - L_cold(T)| > threshold.

### C10: Implicit Regularization
- SGD implicit reg differs for hot vs cold.
- **Expected:** Effect changes with explicit L2 reg.

**Status:** None tested empirically (pilot not run). If pilot were run, expect **several** competing explanations to be supported → Mpemba claim ambiguous.

---

## 4. Literature Evidence Against User Mechanism

### 4.1 Warm-Start Generalization Gap (Ash&Adams 2020, DASH 2024)

**Finding:** High-variance init (hot) converges faster on **train** but generalizes **worse** on **test**.

**Implication:** If user hypothesis Mpemba crossing only on train (not test), it's **overfitting artifact**, not useful phenomenon. DASH (2024) shows cold-start achieves better test accuracy despite slower train convergence.

**Quote (DASH abstract):**
> Cold-starting often achieves better test accuracy compared to warm-starting, while warm-starting requires less time to converge. Ideal initialization requires less time compared to cold-starting.

**Relevance:** User hypothesis predicts hot (high-variance) reaches target faster. But reaching **train target** fast ≠ **test target** fast. If test crossing absent, Mpemba claim fails (C5 competing explanation).

### 4.2 Edge-of-Stability (Cohen et al. 2021)

**Finding:** NN training often enters regime where sharpness λ_max ~ 2/η, loss decreases **non-monotonically** despite classical theory predicting divergence.

**Implication:** Non-monotonic loss trajectories common in NN training — not all are Mpemba effect. Hot-cold crossing may be **EoS interaction** (known phenomenon), not Mpemba (new phenomenon).

**Quote (Cohen et al. abstract):**
> GD on neural networks typically operates in a regime we call the Edge of Stability... the training loss behaves non-monotonically, yet consistently decreases over long timescales.

**Relevance:** User hypothesis predicts crossing due to Fisher geometry / slow-mode amplitude. But if crossing coincides with hot entering EoS (sharpness spike), alternative explanation available (C8).

### 4.3 Fisher Matrix Pathology (Karakida 2019)

**Finding:** FIM in DNNs has **pathological spectrum** — many near-zero eigenvalues, few large outliers. Inverting FIM numerically unstable or infeasible.

**Implication:** User hypothesis mentions "Fisher-Rao distance" — requires FIM^{-1}. This is **infeasible** for DNNs without severe approximations. If distance metric is coordinate-dependent (Euclidean L2), observed crossing may be **coordinate artifact** (C7).

**Quote (Karakida et al.):**
> Both FIMs asymptotically show pathological eigenvalue spectra... a small number of eigenvalues become large outliers depending the width or sample size while the others are much smaller.

**Relevance:** User mechanistic claim (Fisher geometry) relies on metric that cannot be computed exactly in DNNs. Approximations (KL-based distance, L2 proxy) introduce artifacts.

---

## 5. Anticipated Null Findings (Pilot Not Run)

If pilot experiment were executed, we **predict** (based on literature):

### 5.1 Train-Test Mismatch (High Probability)
- **Prediction:** Hot crosses cold on **train loss**, but NOT on **test loss** (or opposite direction).
- **Basis:** Ash&Adams 2020, DASH 2024 (warm-start trades speed for generalization).
- **Outcome if confirmed:** **REJECTED** (overfitting artifact, C5).

### 5.2 Batch-Order Sensitivity (Moderate Probability)
- **Prediction:** Crossing occurs with some batch orders, absent or flips with others.
- **Basis:** Hot init luck with early batches.
- **Outcome if confirmed:** **REJECTED** (batch artifact, C1).

### 5.3 Weak Effect Size (Moderate Probability)
- **Prediction:** Even if crossing occurs, Δτ = (τ_cold - τ_hot) small (e.g., 50 steps / 5000 = 1%).
- **Basis:** Incremental construction (init-based) vs. published (LR-based Liu&Hu).
- **Outcome if confirmed:** **INCONCLUSIVE** (effect present but practically insignificant).

### 5.4 Sharpness Crossing (High Probability)
- **Prediction:** λ_max_hot(0) > λ_max_cold(0), and λ_max_hot crosses below λ_max_cold before distance crossing.
- **Basis:** Cohen et al. 2021 (EoS dynamics), Jastrzebski et al. 2021 (catastrophic Fisher explosion).
- **Outcome if confirmed:** **INCONCLUSIVE** (EoS interaction, C8, mechanism ambiguous).

### 5.5 Negative Control Fails (Low-Moderate Probability)
- **Prediction:** Negative control (same initial loss, same curvature) also shows crossing → trivial mechanism (C4).
- **Basis:** Larger initial loss → larger gradients → faster descent (quadratic bowl intuition).
- **Outcome if confirmed:** **REJECTED** (Fisher geometry not necessary, C4 supported).

---

## 6. Null Result: Experiment Not Run

**Fact:** Pilot experiment code written (`mpemba_experiment.py`) but **NOT executed**.

**Reason:** Terminal decision (`NOT_NOVEL_IN_CLAIMED_FORM`) reached via literature audit + formalization, **before** empirical phase.

**Epistemic status:**
- We **do not know** empirically whether init-based Mpemba crossing occurs.
- We **assign P(crossing exists | Liu&Hu published) ≈ 0.6** (moderately likely, but uncertain).
- Decision is **risk management** (don't burn 20h compute for 60% chance of incremental confirmation), not **empirical proof of absence**.

**Transparency:** Code + prereg + sealed holdout **available**. User or external researchers can run experiment and challenge our decision if they obtain SUPPORTED outcome.

**GOS-I16 (unknown is valid):** We report **UNKNOWN** empirical status, not invented negative result.

---

## 7. Limitations Acknowledged

### 7.1 No Empirical Data
- **Limitation:** Terminal based on literature + formalization, not experiment.
- **Impact:** Cannot rule out empirical surprise (init-based qualitatively different from LR-based).

### 7.2 Formalization Choices
- **Limitation:** FORMALIZATION.md made design choices (distance V1/V2, target Alt 1.3, H_e as init-scale) not explicit in SOURCE_HYPOTHESIS.md.
- **Impact:** Different choices might yield different outcomes. Residual ambiguity.

### 7.3 Scale Dependence
- **Limitation:** Prereg tested 2-layer MLP (small scale). Effect may exist only in large LLMs (Liu&Hu scale).
- **Impact:** Cannot rule out scale-dependent phenomenon.

### 7.4 Mechanism Ambiguity
- **Limitation:** Even if crossing confirmed, mechanism (slow-mode amplitude a₂) not directly measured.
- **Impact:** Competing explanations (C1-C10) remain plausible. Causal inference tentative.

---

## 8. Evidence That Would Change Decision

**Hypothetical:** What evidence would **overturn** `NOT_NOVEL_IN_CLAIMED_FORM` verdict?

### 8.1 Liu & Hu Retracted
If arxiv:2507.04206 retracted (fatal flaw found), user hypothesis novelty restored.

**Probability:** Very low (~0.01). Paper is mathematically sound (Fokker-Planck analysis standard in stochastic thermo).

### 8.2 Qualitative Difference Found
If init-based construction shows **qualitatively different** behavior than LR-based (e.g., opposite crossing direction, different curvature dependence), narrow novelty established.

**Test:** Run both constructions (init-based and LR-based) in same architecture, compare.

**Status:** Not tested. User hypothesis did not claim qualitative difference, only existence of effect.

### 8.3 User Explicitly Narrows Claim
If user **amends** SOURCE_HYPOTHESIS.md to state: "Novelty is **not** existence of Mpemba in NN training (Liu&Hu already showed this), but **specific construction** (init-based at fixed LR, not LR-schedule-based)."

**Impact:** Narrow novelty claim testable. But original SOURCE_HYPOTHESIS.md does **not** state this — general claim fails.

---

## 9. Honest Uncertainty Quantification

| Claim | P(True) | Evidence Basis |
|-------|---------|----------------|
| Mpemba exists in NN training (general) | **~0.9** | Liu&Hu 2025 (theoretical), high prior plausibility |
| Mpemba exists in init-based construction (fixed LR) | **~0.6** | Not tested, plausible extrapolation from Liu&Hu |
| Crossing survives test set (not just train) | **~0.4** | Warm-start literature suggests train-test mismatch |
| Crossing robust to batch order | **~0.5** | Unknown, batch-order effects common in SGD |
| Crossing survives negative control (C4) | **~0.6** | Fisher geometry mechanism plausible but not proven |
| User hypothesis novel (in stated form) | **~0.05** | Liu&Hu published core claim 9 months prior |

**Interpretation:** We are **highly confident** (P ~ 0.95) that general Mpemba claim is not novel. We are **moderately uncertain** (P ~ 0.6) about narrow init-based construction. We report this uncertainty honestly (GOS-I16, GOS-I23).

---

## 10. Recommendations for Future Work

### 10.1 Reproduce Liu & Hu (High Priority)
- **Task:** Replicate Liu&Hu valley-river Mpemba effect in real LLM training (not just toy model).
- **Why:** Liu&Hu is theoretical + toy model. Empirical replication on GPT-2 / Llama-scale missing.
- **Value:** Reproducibility > incremental novelty (init-based variant).

### 10.2 Test Generalization (High Priority)
- **Task:** Check if Liu&Hu Mpemba crossing occurs on **test loss** (not just train).
- **Why:** Warm-start literature (DASH 2024) shows train-test tradeoff. If Mpemba only on train, it's overfitting artifact.
- **Value:** Distinguishes useful phenomenon from artifact.

### 10.3 Falsify Liu & Hu (High Priority)
- **Task:** Test **counterevidence** for Liu&Hu theory:
  - Does effect disappear with batch shuffling?
  - Does effect disappear without valley-river structure (flat loss landscape)?
  - Does effect disappear with momentum (Adam)?
- **Why:** Falsification > confirmation (Popperian epistemology).
- **Value:** Strengthens theory if survives, or reveals boundaries if fails.

### 10.4 Init-Based Construction (Medium Priority)
- **Task:** Run user hypothesis experiment (pilot + confirmatory) with provided code.
- **Why:** Narrow novelty claim (init-based vs LR-based) not tested.
- **Value:** Incremental contribution (if SUPPORTED). Lower priority than 10.1-10.3.

---

**END OF COUNTEREVIDENCE**

**Summary:** Primary counterevidence = Liu&Hu 2025 prior publication. Secondary = formalization barriers (ILL_POSED). Tertiary = 10 competing explanations not ruled out (no empirical test). Honest uncertainty reported (GOS-I16, GOS-I23).
