# Y19-H4 — Size vs entropy decomposition

**Prior:** Y19-H3 → `SUPPORTED` (`H_h2_robust`).  
**Narrow claim so far:** size/entropy combo beats activity-only under robustness gates — **not** yet “entropy predicts transients”.

## Question (unknown a priori)

> At fixed system size, does **entropy** retain predictive value beyond activity;  
> or is the H2/H3 effect explained mainly by **N**?

## Gates (no new fancy features)

| Gate | Protocol |
|------|----------|
| **A N-matched** | Within each `N∈{16,20,24}`, `activity+entropy` vs `activity`; ≥2 powered N must meet MCID |
| **B residualized entropy** | `residual_entropy = entropy − E[entropy‖N,activity]`; activity+residual vs activity MCID **and** nested `activity+N+entropy` vs `activity+N` MCID |
| **C leave-one-N-out** | Train on other sizes, hold one N; ≥2 folds keep entropy MCID |

## Competing hypotheses

1. **H_entropy_survives_n_control** — A∧B∧C PASS  
2. **H_effect_is_mostly_n** — A or B FAIL (entropy dies under N control)  
3. **H_conditional_on_n** — mixed / underpowered  

## Seeds

Train 4000–4299 · Hold 8000–8149 · balanced N panel · disjoint from H1–H3.

## Explicit non-claim

Even if SUPPORTED: only “entropy retains OOS signal beyond activity under N controls” — not a general transient theory.
