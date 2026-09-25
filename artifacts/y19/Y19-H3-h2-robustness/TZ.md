# Y19-H3 — Robustness of H2 size/entropy signal

**Prior:** Y19-H2 → `SUPPORTED` (`H_size_entropy_add_signal`).  
**Question (unknown a priori):** Does that gain survive activity matching, unseen system size, and both K regimes?

## Why this test

H2 could mean three different things:

1. size/entropy reflect structure before long transients  
2. they are mostly a **size proxy**  
3. the effect is **local** to the training distribution / one regime  

H3 separates these with three locked gates (all must PASS for SUPPORTED).

## Gates

| Gate | Protocol |
|------|----------|
| **A activity-matched** | Train activity tertile cuts; on in-family hold, ≥2 powered tertiles must show `Brier_full/Brier_activity ≤ 0.90` |
| **B unseen-size** | Train `N∈{16,20}` only; sealed hold `N=24`; MCID vs activity |
| **C regime** | Both powered `K=2` and `K=3` hold slices must meet MCID |

## Competing hypotheses

1. **H_h2_robust** — A∧B∧C PASS  
2. **H_size_proxy_or_fragile** — A or B FAIL  
3. **H_regime_local** — only C FAIL, or underpowered outside distribution  

## Seeds

- Train: 3000–3239  
- Hold match (A/C): 7200–7319  
- Hold unseen N (B): 7000–7119  
- Disjoint from H1/H2/Y17  

## Non-goals

Does not reopen H1 spectral claim. Does not start LH 96m/48h. Not M1.5.
