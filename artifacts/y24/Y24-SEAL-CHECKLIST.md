# Y24 Seal Checklist — prepare experiment before unseal

**Status:** binding sequence  
**Do not skip steps. Do not execute arms before step 7 completes.**

```text
1. Collect OSS task corpus (public licenses) into DEV draft
2. Score complexity features with Y24-COMPLEXITY-RUBRIC (a priori)
3. Assign danger labels + failure_class (for memory pairs)
4. Ensure ≥30% of benign are benign_suspicious
5. Split DEV vs HOLDOUT (holdout unseen to arm builders)
6. Freeze HOLDOUT → status FROZEN_UNSEEN + sha256 manifest
7. Freeze experiment SHA under PREREG_LOCKED + rubric/cost/isolation locks
8. Implement / freeze stubs A/B/C + cost ledger (comparable resources)
9. Isolation attestation: C/memory builders certify no sealed access
10. ONLY THEN unseal for execution
11. Score blind → COMPARISON_REPORT → KEEP/REJECT/INCONCLUSIVE
```

## Current progress

| Step | Status |
|------|--------|
| 1 corpus collect | DONE |
| 2 stratum scoring | DONE (a priori) |
| 3 labels | DONE |
| 4 benign_suspicious fraction | DONE (≥0.3 holdout) |
| 5 DEV/HOLDOUT split | DONE |
| 6 holdout freeze | FROZEN then UNSEALED_FOR_EXECUTION |
| 7 experiment SHA | FROZEN (Y24_EXPERIMENT_SHA.txt) |
| 8 arm stubs | HEURISTIC_HARNESS_v1 executed |
| 9 isolation attestation | DONE |
| 10 unseal execution | DONE |
| 11 decision | SCORED (see Y24_DECISION.md) |

## Thresholds

```text
MUST NOT MOVE after holdout freeze / SHA freeze
MCID amend only via documented pilot BEFORE unseal
```
