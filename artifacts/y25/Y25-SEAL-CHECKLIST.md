# Y25 Seal Checklist

**Protocol:** `Y25-MV-v1`  
**Campaign status:** `PREREG_LOCKED_PREP_CORPUS`

| # | Step | Status |
|---|------|--------|
| 1 | Collect real OSS failure incident pairs (first + unseen variant) | NOT_STARTED |
| 2 | A-priori failure_class labels; different repo/patch for variants | NOT_STARTED |
| 3 | Split DEV / HOLDOUT (≥50% pairs holdout); blind public refs | NOT_STARTED |
| 4 | Seal holdout (`FROZEN_UNSEEN` + SHA256) | NOT_SEALED_YET |
| 5 | Freeze experiment SHA | NOT_FROZEN |
| 6 | Implement W0/W1 harness stubs + shared cost ledger | STUB_SKELETON |
| 7 | Isolation attestation for W1 | BLANK |
| 8 | Unseal execution | BLOCKED |
| 9 | Score KEEP/REJECT/INCONCLUSIVE → `Y25_DECISION.md` | BLOCKED |

Do not start arms until 1–7 done. Do not reopen Y24.
