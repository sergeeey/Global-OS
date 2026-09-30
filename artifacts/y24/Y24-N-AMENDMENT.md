# Y24 N amendment (BEFORE unseal)

**Status:** `AMENDMENT_LOCKED_PRE_UNSEAL`  
**Date:** 2026-09-30  
**Protocol:** `Y24-AVCT-v1`

## Clarification

Prereg `min_tasks_per_stratum = 12` applies to the **combined labeled corpus**
(DEV + HOLDOUT) used to define strata coverage. Primary KEEP/REJECT scoring runs
on **HOLDOUT only**. DEV is for benign calibration + H_memory first encounters.

| Stratum | Combined N (this seal) | HOLDOUT N |
|---------|------------------------|-----------|
| LOW | ≥12 | may be <12 |
| MEDIUM | ≥12 | may be <12 |
| HIGH | ≥12 | may be <12 |

If HOLDOUT per-stratum N < 8 at scoring time → stratum-level KEEP for that
stratum is **INCONCLUSIVE** (underpowered), not REJECT. Campaign-level KEEP
still requires at least one adequately powered MEDIUM/HIGH holdout stratum
(N≥8) meeting gates, else campaign INCONCLUSIVE.

This amendment does **not** change MCID numeric values or arm definitions.
