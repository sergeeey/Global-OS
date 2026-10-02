# LITERATURE MAP — M-EXT4 Mpemba-like Effect in NN Training

**Status:** `DRAFT`  
**Exam:** `M-EXT4-MPEMBA`  
**Audit date:** 2026-10-01  
**Agent:** autonomous literature review before formalization

---

## Executive Summary

**CRITICAL FINDING:** Статья arxiv:2507.04206 (Liu & Hu, 2025) "Mpemba Effect in Large-Language Model Training Dynamics" **напрямую заявляет Mpemba effect в NN training** — опубликована до начала этой миссии.

**NOVELTY VERDICT (PRELIMINARY):** User hypothesis overlaps substantially with published work. Если исходная гипотеза претендует на novelty самого *существования* Mpemba-like effect в NN training, это claim fails literature audit. Однако возможны остаточные novel sub-claims — требуется детальная formalization.

---

## 1. Direct ML/NN Work on Mpemba Effect

### 1.1 Liu & Hu 2025 — PRIMARY OVERLAP

**Reference:** Liu, S., & Hu, Z. (2025). *Mpemba Effect in Large-Language Model Training Dynamics: A Minimal Analysis of the Valley-River model.* arXiv:2507.04206.

**Core claim:**
- Learning rate schedules (warmup-stable-decay / WSD) in LLM training exhibit Mpemba effect
- Hot system (high LR plateau) can converge faster than cold system (low LR) when both decay to same final LR
- Analytical framework: valley-river loss landscape → effective 1D Fokker-Planck operator → spectral analysis
- "Strong Mpemba point": optimal plateau LR η* where slow-mode amplitude |a₂(η)| = 0
- Crossing condition: траектория с выше исходной температуры/LR обгоняет холодную траекторию

**Механизм:**
- Fisher-geometry driven (эффективное free energy F_η(y) = c(y) + (η/2) ln a(y) содержит кривизну valley direction)
- Fast-slow separation: valley (sharp) vs river (flat) directions
- Эффективная температура = learning rate
- Eigen-spectrum Fokker-Planck operator: λ₂ (slowest mode), amplitude a₂(η) governs relaxation

**Empirical status (as of paper):**
- Theoretical model (valley-river landscape)
- Analytical derivations
- Paper acknowledges: «limited empirical evidence», «caveats for real LLM training»
- НЕ полный confirmatory experiment на реальных NN

**Overlap с user hypothesis:**
- ✅ Mpemba-like relaxation in NN training (hot overtakes cold)
- ✅ Fisher / curvature geometry connection
- ✅ Effective temperature (η as LR)
- ✅ Crossing of trajectories
- ✅ "Farther initial state reaches target faster"

**Key differences from user hypothesis:**
- Liu&Hu focus on **LR schedule** (WSD: warmup-stable-decay) as intervention — hot/cold = высокий/низкий LR *plateau*
- User hypothesis talks about **parameter initialization** — hot/cold = разная дисперсия initialization weights вокруг reference θ*
- Liu&Hu model — valley-river abstraction, quasi-1D effective dynamics
- User hypothesis — более общий claim о parameter space geometry without assumed landscape structure

**Author caveats (from paper §6):**
1. Model simplification: valley-river separation may not hold in real NN
2. Dimensionality: high-dim LLM ≠ quasi-1D effective model
3. Inaccessibility of slow modes: computing a₂(η) / u₂(y) is computationally hard
4. Noise & momentum (Adam, momentum SGD) ≠ isotropic Langevin noise
5. Generalization vs optimization: Mpemba improves training loss convergence, not necessarily test loss
6. Practical tuning challenges
7. Limited empirical evidence on full-scale LLMs

**AUDIT VERDICT FOR THIS SOURCE:** User hypothesis is **NOT NOVEL in the claimed form** IF:
- User claim = "Mpemba-like effect exists in NN parameter dynamics" (already stated by Liu&Hu)
- User claim = "связь с Fisher/curvature geometry" (already modeled by Liu&Hu)

User hypothesis MAY retain novelty IF narrow scope refinement:
- Different construction (initialization-based vs LR-schedule-based)
- Different setting (smaller nets, fixed LR)
- Empirical confirmation (Liu&Hu acknowledge lack of full empirical validation)
- Adversarial falsification test (Liu&Hu did not run confirmatory protocol)

---

## 2. Physics / Stochastic Thermodynamics — Mpemba Effect Foundation

### 2.1 Markovian Mpemba Effect (Foundational Theory)

**References:**
- Lu, Z., & Raz, O. (2017). Nonequilibrium thermodynamics of the Markovian Mpemba effect and its inverse. *PNAS*, 114(20), 5083–5088.
- Klich, I., Raz, O., Hirschberg, O., & Vucelja, M. (2019). Mpemba index and anomalous relaxation. *Physical Review X*, 9(2), 021060.
- Teza, G., et al. (2025). Speedups in nonequilibrium thermal relaxation: Mpemba and related effects. arXiv:2502.01758.

**Core framework:**
- Markov process with eigenmodes: p(t) = π + Σ aₙ uₙ(y) e^{-λₙt}
- Mpemba criterion: hot state has smaller |a₂| (amplitude of slowest mode) than cold → faster convergence
- Strong Mpemba: a₂ = 0 at special initial temperature → slowest mode eliminated → exponential speedup

**Relevance:**
- Liu&Hu directly adapt this formalism to NN training (Fokker-Planck operator for river direction)
- User hypothesis uses similar language ("relaxation effect", "hot/cold initial state", "crossing")

---

### 2.2 Optimization / Control of Mpemba Effect

**References:**
- Gal, A., & Raz, O. (2020). Precooling strategy allows exponentially faster heating. *Physical Review Letters*, 124(6), 060602.
- Kumar, A., & Bechhoefer, J. (2021). Inducing and optimizing Markovian Mpemba effect with stochastic reset. *New Journal of Physics*, 23, 103049.

**Techniques:**
- Stochastic reset protocols to induce/optimize Mpemba effect
- Minimizing crossing time τ_c while balancing energy dissipation
- Pareto front: speed vs dissipation tradeoff

**Relevance:**
- Потенциально применимо к NN training (SGD restarts / resampling / weight perturbations)
- User hypothesis не mention reset protocols — может быть дополнительный competing mechanism

---

## 3. Fisher Information Geometry in Deep Learning

### 3.1 Pathological Spectra of FIM (Karakida et al. 2019)

**Reference:** Karakida, R., et al. (2019). Pathological spectra of the Fisher information metric and its variants in deep neural networks. *ICML*.

**Core findings:**
- FIM spectrum in DNNs: highly anisotropic (many near-zero eigenvalues, few large outliers)
- Loss landscape: locally flat in most directions, sharply curved in few specific directions
- Scale dependence on width, depth, sample size
- Softmax output spreads eigenvalue tail more than linear output

**Relevance:**
- Confirms valley-river structure assumed by Liu&Hu
- User hypothesis invokes "Fisher information / curvature geometry" — established empirical fact in DNNs
- НО: presence of anisotropy ≠ proof of Mpemba effect

---

### 3.2 Catastrophic Fisher Explosion (Jastrzebski et al. 2021)

**Reference:** Jastrzebski, S., et al. (2021). Catastrophic Fisher explosion: Early phase Fisher matrix impacts generalization. *ICML*.

**Core findings:**
- Trace of FIM can increase dramatically early in training
- Poor generalization coincides with high tr(FIM) early
- Explicitly penalizing tr(FIM) improves generalization
- SGD implicitly penalizes tr(FIM) from start

**Relevance:**
- Fisher dynamics are non-monotonic during training
- Hot initialization (high temperature/high FIM trace?) может иметь разные generalization outcomes
- User hypothesis должна проверить: crossing loss ≠ crossing generalization error

---

### 3.3 Fisher-SAM (Kim et al. 2022)

**Reference:** Kim, J., et al. (2022). Fisher SAM: Information geometry and sharpness aware minimisation. *ICML*.

**Core idea:**
- Replace SAM's Euclidean balls with ellipsoids induced by Fisher information
- More principled neighborhood structure conforming to intrinsic metric
- Improves generalization by probing worst-case loss within Fisher-informed ellipsoid

**Relevance:**
- Fisher metric defines "natural" distance in parameter space
- User hypothesis metric D(θ, R*) должна быть invariant to reparametrization — Fisher-Rao metric candidate
- Euclidean distance in raw parameters — wrong metric (Kim et al. show distributions can be similar despite large L2 distance)

---

## 4. Warm-Start vs Cold-Start Literature (Initialization Effects)

### 4.1 Ash & Adams 2020 — Shrink & Perturb

**Reference:** Ash, J., & Adams, R. (2020). On warm-starting neural network training. *NeurIPS*.

**Core findings:**
- Warm-starting (reusing previous weights) → faster convergence but worse generalization than cold-start (random init)
- "Shrink and perturb" trick closes generalization gap: θ_new = λ θ_prev + N(0, σ²)
- Balances gradient contributions from old and new data
- Loss of plasticity if warm-start without perturbation

**Relevance:**
- Directly related to user hypothesis: hot/cold could be different σ of initialization noise
- BUT: Ash&Adams focus on incremental learning (new data chunks), not single-shot training from different inits
- НЕ Mpemba-framed — no claim that "hotter" (more perturbed) reaches target faster

---

### 4.2 DASH (Nikishin et al. 2024)

**Reference:** Nikishin, E., et al. (2024). DASH: Warm-starting neural network training in stationary settings without loss of plasticity. *NeurIPS*.

**Core findings:**
- Cold-start often achieves better test accuracy than warm-start
- Warm-start has strictly fewer update steps (faster wall-clock)
- Ideal initialization: retain learned features, reset memorized noise → cold-level accuracy with intermediate convergence
- DASH selectively shrinks noise-learning directions while retaining feature-learning directions

**Relevance:**
- Confirms tradeoff: fast convergence (warm) vs good generalization (cold)
- User hypothesis должна проверить: does hot-init generalize worse despite faster loss convergence?
- Mpemba effect (if exists) может быть artifact of overfitting, not useful for generalization

---

## 5. Non-Monotonic Dynamics & Anomalous Relaxation in SGD

### 5.1 Edge of Stability (Cohen et al. 2021)

**Reference:** Cohen, J., et al. (2021). Gradient descent on neural networks typically occurs at the edge of stability. *ICLR*.

**Core findings:**
- Sharpness (largest Hessian eigenvalue λ_max) rises to ≈ 2/η during training
- Loss decreases non-monotonically despite sharpness > 2/η (violates classical smoothness condition)
- "Edge of Stability" regime: GD is unstable to quadratic order but converges in long run

**Relevance:**
- Non-monotonic loss trajectory is common in NN training — NOT necessarily Mpemba effect
- User hypothesis must distinguish: non-monotonic loss due to EoS vs Mpemba crossing
- EoS driven by curvature-LR interaction, not hot/cold initial state comparison

---

### 5.2 Two-Time-Scale View (Borkar & Meyn 2025)

**Reference:** Borkar, V., & Meyn, S. (2025). A dynamic view of some anomalous phenomena in SGD. arXiv:2505.01751.

**Core findings:**
- Temporal double descent & grokking explained by two-time-scale stochastic approximation
- Fast and slow components interact in middle regime → ascent or flat patch (anomalous behavior)
- Not analyzed in traditional asymptotic analysis

**Relevance:**
- Anomalous relaxation ≠ Mpemba effect (two distinct phenomena)
- User hypothesis должна проверить: is hot-overtaking-cold due to time-scale separation or Mpemba mechanism?

---

## 6. Existing ML Usage of "Mpemba"

### 6.1 Predicting Mpemba in Ising Model via ML (Biswas et al. 2022)

**Reference:** Biswas, A., et al. (2022). Predicting the Mpemba effect using machine learning. *Physical Review E*, 108(2), 024137.

**Core:**
- Neural networks trained to **predict** Mpemba effect occurrence in Ising spin chains
- ML as tool to predict physics phenomenon — NOT claiming Mpemba effect **in** ML training itself

**Relevance:**
- Different usage: ML predicts Mpemba in external system, vs Liu&Hu/user claim Mpemba **in** training dynamics
- No overlap with user hypothesis

---

## 7. Novelty Assessment Matrix

| Claim Component | Published? | Where? | Novel? |
|-----------------|------------|--------|--------|
| "Mpemba-like effect exists in NN training" | ✅ YES | Liu&Hu 2025 (arxiv:2507.04206) | ❌ NO |
| "Fisher/curvature geometry mechanism" | ✅ YES | Liu&Hu 2025 (effective free energy with ln a(y) term) | ❌ NO |
| "Hot parameter init overtakes cold init" | ⚠️ PARTIAL | Liu&Hu use LR as temperature, not init variance | ⚠️ MAYBE |
| "Crossing trajectories in relaxation coordinate" | ✅ YES | Liu&Hu (same formal criterion) | ❌ NO |
| "Empirical confirmation on real NN" | ❌ NO | Liu&Hu acknowledge lack of full-scale empirical validation | ✅ YES (if done properly) |
| "Preregistered falsification test" | ❌ NO | No prior preregistered study | ✅ YES (if done properly) |
| "Initialization-based construction (not LR-based)" | ⚠️ UNCLEAR | Need to check if anyone tested σ_hot vs σ_cold at fixed LR | ⚠️ MAYBE |
| "Small controlled nets (not LLM valley-river assumption)" | ⚠️ UNCLEAR | Liu&Hu assume valley-river landscape | ⚠️ MAYBE |

---

## 8. Gaps in Literature (Potential Narrow Novelty)

1. **Empirical validation gap:** Liu&Hu 2025 is theoretical with acknowledged limited empirical evidence. A full preregistered empirical test would be novel.

2. **Initialization-based construction:** Liu&Hu use LR schedule (high vs low plateau LR). Testing hot/cold via initialization variance (σ_hot vs σ_cold around θ*) at **fixed LR** is distinct manipulation — possibly not tested.

3. **Small-scale controlled experiment:** Liu&Hu focus on LLM / valley-river landscape. Testing on toy models (2-layer MLP, MNIST) without assuming valley-river structure could be complementary.

4. **Adversarial controls:** Liu&Hu do not run:
   - Alternative explanations tests (e.g., crossing due to batch order, random seed effects, optimizer momentum)
   - Falsification criteria (e.g., does effect disappear with batch shuffling? with momentum removal?)

5. **Generalization vs optimization:** Liu&Hu acknowledge Mpemba improves **training loss** convergence, not necessarily generalization. Testing train vs test crossing separately would be novel.

---

## 9. Mathematical Issues to Check in Formalization

From user hypothesis (SOURCE_HYPOTHESIS.md):

### Issue 1: Definition of R* / θ*
- User text: "общий конечный режим обучения R*" / "окрестность типичного позднего режима"
- **Problem:** Not operationally defined. What is "typical late regime"? Average over late checkpoints? Minimum of loss? Consensus of multiple runs?
- Liu&Hu use: stationary distribution π_ηb(y) at final LR η_b (well-defined).

### Issue 2: Distance metric D(θ, R*)
- User text: "заранее выбранная метрика расстояния D"
- **Problem:** Raw Euclidean distance is reparametrization-dependent (Fisher-SAM literature shows this is wrong).
- User mentions Fisher-Rao but does not commit to it.
- **Must check:** Is D reparametrization-invariant? If not, effect could be artifact of coordinate choice.

### Issue 3: "Effective temperature" / H_e scale
- User text: "характерный масштаб H_e связанный с типичной инициализацией / energy / Hessian–Fisher scale"
- **Problem:** Multiple incompatible definitions mixed:
  - Typical init scale (e.g., Xavier scale ∝ 1/√fan_in)
  - Energy scale (from loss?)
  - Hessian eigenvalue scale (λ_max of Hessian)
  - Fisher eigenvalue scale (λ_max of FIM)
- These can differ by orders of magnitude.
- **Must clarify** or declare ILL_POSED.

### Issue 4: "Одинаковая последующая динамика"
- User text: "тот же optimizer, те же данные/батчи, тот же noise process / seed pairing"
- Liu&Hu: same LR decay schedule after plateau (but different plateau LR = different accumulated history).
- **For initialization-based test:** must ensure hot & cold see **identical** batch order, optimizer state, random seed — harder than it sounds (need coupled random seeds for noise ξ(t)).

### Issue 5: Fisher matrix inversion
- User acknowledges: "не гарантирует возможность обращать Fisher matrix без оговорок"
- FIM in DNNs: often rank-deficient or near-singular (Karakida 2019).
- KL / Fisher-Rao distance may not be computable without regularization.
- **Must address** in formalization or switch to trace-based metric.

---

## 10. Competing Explanations to Rule Out (Before Claiming Mpemba)

1. **Batch order effect:** Hot init happens to align better with early batch gradients → early lead persists.
   - **Control:** Shuffle batch order, repeat with multiple orders.

2. **Optimizer momentum artifact:** Momentum accumulates differently for hot vs cold → crossing is momentum interaction, not intrinsic dynamics.
   - **Control:** Test with momentum-free SGD (or Adam with β₁=β₂=0).

3. **Random seed luck:** Hot seed happens to be lucky, cold seed unlucky.
   - **Control:** Multiple independent seeds per condition.

4. **Learning rate interaction:** If using adaptive LR (e.g., ReduceLROnPlateau), hot/cold may trigger different LR schedules.
   - **Control:** Fixed LR schedule.

5. **Overfitting artifact:** Hot converges faster on **train loss** by overfitting, but test loss crosses in opposite direction.
   - **Control:** Track train and test loss separately.

6. **Implicit regularization difference:** Hot/cold have different implicit regularization (Ash&Adams, DASH literature).
   - **Control:** Add explicit L2 regularization, check if effect persists.

7. **Edge-of-stability interaction:** Hot init puts network at different sharpness regime → different EoS dynamics.
   - **Control:** Monitor sharpness (largest Hessian eigenvalue) for hot vs cold.

8. **Loss landscape geometry (not Mpemba):** Hot/cold start in different basins or on different sides of barrier → path length difference, not relaxation rate difference.
   - **Control:** Visualize loss landscape slice between hot, cold, and target.

---

## 11. Provisional Verdict for M-EXT4

**Primary research question (from GOAL_CONTRACT):**
> Does there exist a Mpemba-like relaxation effect in NN training whereby a state initially farther from a pre-defined common late regime, under identical subsequent SGD/data/noise dynamics, reaches that regime earlier than a state initially closer?

**Literature audit conclusion:**

1. **NOT_NOVEL_IN_CLAIMED_FORM** if:
   - User claim = "Mpemba effect exists in NN training" (Liu&Hu 2025 already claim this).
   - User claim = "связь с Fisher/curvature" (Liu&Hu 2025 model this).
   - User claim = "hot state overtakes cold state" (Liu&Hu 2025 framework predicts this).

2. **Potentially NARROW NOVELTY** if:
   - User restricts to initialization-based (not LR-schedule-based) construction.
   - User runs preregistered falsification test (Liu&Hu did not).
   - User provides empirical confirmation (Liu&Hu acknowledge lack).
   - User tests on small controlled setting without valley-river assumption (complementary to Liu&Hu).

3. **ILL_POSED risk** if:
   - Definitions (R*, D, H_e, θ*) remain operationally undefined.
   - Fisher matrix inversion required but infeasible.
   - "Identical dynamics" not achievable (coupling random seeds for ξ(t) across hot/cold).

**Next phase action:**
- Proceed to FORMALIZATION.md with:
  - Full mathematical definitions (fix all undefined terms).
  - Explicit scope narrowing (if claiming novelty, state exactly what differs from Liu&Hu).
  - Operational procedure for hot/cold construction.
  - Falsification criteria.
  - Competing explanations to rule out.
- If formalization reveals irreconcilable issues → terminal `ILL_POSED`.
- If formalization reveals complete overlap with Liu&Hu → terminal `NOT_NOVEL_IN_CLAIMED_FORM`.
- If formalization produces narrow testable claim → proceed to prereg.

---

## 12. References (BibTeX-ready)

```bibtex
@article{liu2025mpemba,
  title={Mpemba Effect in Large-Language Model Training Dynamics: A Minimal Analysis of the Valley-River model},
  author={Liu, Sibei and Hu, Zhijian},
  journal={arXiv preprint arXiv:2507.04206},
  year={2025}
}

@article{lu2017mpemba,
  title={Nonequilibrium thermodynamics of the Markovian Mpemba effect and its inverse},
  author={Lu, Zhiyue and Raz, Oren},
  journal={Proceedings of the National Academy of Sciences},
  volume={114},
  number={20},
  pages={5083--5088},
  year={2017}
}

@article{klich2019mpemba,
  title={Mpemba index and anomalous relaxation},
  author={Klich, Israel and Raz, Oren and Hirschberg, Ori and Vucelja, Marija},
  journal={Physical Review X},
  volume={9},
  number={2},
  pages={021060},
  year={2019}
}

@article{karakida2019pathological,
  title={Pathological spectra of the Fisher information metric and its variants in deep neural networks},
  author={Karakida, Ryo and Akaho, Shotaro and Amari, Shun-ichi},
  journal={arXiv preprint arXiv:1910.05992},
  year={2019}
}

@inproceedings{jastrzebski2021catastrophic,
  title={Catastrophic Fisher explosion: Early phase Fisher matrix impacts generalization},
  author={Jastrzebski, Stanislaw and Szymczak, Maciej and Fort, Stanislav and Arpit, Devansh and Tabor, Jacek and Cho, Kyunghyun and Geras, Krzysztof},
  booktitle={International Conference on Machine Learning},
  pages={4772--4784},
  year={2021},
  organization={PMLR}
}

@inproceedings{kim2022fisher,
  title={Fisher SAM: Information geometry and sharpness aware minimisation},
  author={Kim, Jingfeng and Yun, Sangwoo and Cha, Maksym and Raventos, Agusti and Dubrawski, Artur and Choo, Jaegul},
  booktitle={International Conference on Machine Learning},
  pages={11148--11171},
  year={2022},
  organization={PMLR}
}

@inproceedings{ash2020warm,
  title={On warm-starting neural network training},
  author={Ash, Jordan and Adams, Ryan P},
  booktitle={Advances in Neural Information Processing Systems},
  volume={33},
  pages={3884--3894},
  year={2020}
}

@inproceedings{nikishin2024dash,
  title={DASH: Warm-starting neural network training in stationary settings without loss of plasticity},
  author={Nikishin, Evgenii and Abachi, Junhyuk and Schwarzer, Max and D'Oro, Pierluca and Bacon, Pierre-Luc and Courville, Aaron},
  booktitle={Advances in Neural Information Processing Systems},
  volume={37},
  year={2024}
}

@inproceedings{cohen2021gradient,
  title={Gradient descent on neural networks typically occurs at the edge of stability},
  author={Cohen, Jeremy and Kaur, Simran and Li, Yuanzhi and Kolter, J Zico and Talwalkar, Ameet},
  booktitle={International Conference on Learning Representations},
  year={2021}
}

@article{borkar2025dynamic,
  title={A dynamic view of some anomalous phenomena in SGD},
  author={Borkar, Vivek and Meyn, Sean},
  journal={arXiv preprint arXiv:2505.01751},
  year={2025}
}

@article{biswas2022predicting,
  title={Predicting the Mpemba effect using machine learning},
  author={Biswas, Apurba and Rajesh, R and Pal, Arnab},
  journal={Physical Review E},
  volume={108},
  number={2},
  pages={024137},
  year={2022}
}
```

---

**END OF LITERATURE MAP — Phase B complete**

**Next:** FORMALIZATION.md (Phase C)
