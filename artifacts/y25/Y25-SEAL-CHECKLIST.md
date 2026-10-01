# Y25 Seal Checklist

**Protocol:** `Y25-MV-v1`  
**Campaign status:** `PREREG_LOCKED_PREP_CORPUS`

| # | Step | Status |
|---|------|--------|
| 1 | Collect real OSS failure incident pairs (first + unseen variant) | DONE (≥24) |
| 2 | A-priori failure_class labels; different repo/patch for variants | DONE |
| 3 | Split DEV / HOLDOUT (≥50% pairs holdout); blind public refs | DONE |
| 4 | Seal holdout (`FROZEN_UNSEEN` + SHA256) | DONE then UNSEALED |
| 5 | Freeze experiment SHA | DONE |
| 6 | Implement W0/W1 harness stubs + shared cost ledger | DONE |
| 7 | Isolation attestation for W1 | DONE |
| 8 | Unseal execution | DONE |
| 9 | Score KEEP/REJECT/INCONCLUSIVE → `Y25_DECISION.md` | DONE |

Do not start arms until 1–7 done. Do not reopen Y24.
