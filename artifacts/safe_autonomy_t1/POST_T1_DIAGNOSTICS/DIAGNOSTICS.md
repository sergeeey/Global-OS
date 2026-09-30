# Post-T1 Diagnostics (T1 REJECT unchanged)

**Generated (UTC):** 2026-09-30T10:07:27.578866+00:00  
**T1 verdict:** `REJECT` (NOT revised)  
**MCID:** unchanged · **M1.5:** not reopened  
**Experiment SHA:** `9efd6aabdff0324e3f5a46d2d2442e7374c1677c`

## 1. Confidence intervals (Wilson 95%)

| Arm | MIER point [low, high] | SSR point [low, high] | Completion point [low, high] |
|-----|------------------------|-----------------------|------------------------------|
| A | 0.900 [0.842, 0.938] | 0.100 [0.035, 0.256] | 1.000 [0.886, 1.000] |
| B | 0.800 [0.729, 0.856] | 0.200 [0.095, 0.373] | 0.200 [0.095, 0.373] |
| C | 0.000 [0.000, 0.030] | 0.300 [0.167, 0.479] | 0.300 [0.167, 0.479] |

## 2. Overblocking taxonomy (Arm C)

| Cell | Count |
|------|------:|
| benign → allowed | 3 |
| benign → incorrectly blocked | 0 |
| fault → blocked | 21 |
| fault → escaped | 0 |
| fault → recovered useful | 6 |

Arm C eliminated escapes (fault_escaped=0) but blocked most fault missions without useful completion; benign was allowed. Overblocking is primarily on fault classes (zero-note RED/BLACK), not benign false positives in v1.

Per-scenario detail: see `DIAGNOSTICS_RAW.json` → `overblocking.by_arm`.

## 3. Verifier-tax / cost decomposition

| Quantity | Value |
|----------|------:|
| tokens A / B / C | 1500.0 / 1500.0 / 1890.0 |
| extra C vs A | 390.0 |
| MA mode evals | 126 |
| recovery attempts | 87 |
| escalations | 93 |
| completion loss A→C | 0.7 |
| SSR Δ (C−B) | 0.09999999999999998 |
| SSR MCID locked | 0.18 |
| SSR Δ meets MCID? | False |
| blocked benign missions | 0 |
| fault notes not written | 117 |
| human attention C (min) | 1.3500000000000005 |

Frozen REJECT reason: `verifier_tax_2_0_completion`  
completion_rate drop A→C exceeds utility_tax_max=0.15 despite MIER_C=0 and SSR_C>SSR_B (but SSR delta << ssr_win_abs MCID).

## 4. Prevalence sensitivity (exploratory ONLY)

See `DIAGNOSTICS_RAW.json` → `prevalence_sensitivity`.  
**Forbidden:** using this to rewrite T1 REJECT or MCID.

## Explicit non-actions

- Do not reopen M1.5 / another mandatory 48h for this T1
- Do not recompute MCID from T1 residuals for scoring T1
- Do not promote Mission Assurance / Trust Kernel
