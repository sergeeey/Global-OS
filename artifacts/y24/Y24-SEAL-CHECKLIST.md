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
| 1 corpus collect | NOT_STARTED (schema ready) |
| 2 stratum scoring | RUBRIC_LOCKED; scoring NOT_STARTED |
| 3 labels | NOT_STARTED |
| 4 benign_suspicious fraction | GATE_LOCKED in prereg |
| 5 DEV/HOLDOUT split | NOT_STARTED |
| 6 holdout freeze | NOT_SEALED_YET |
| 7 experiment SHA | NOT_FROZEN |
| 8 arm stubs | STUB_SKELETON (refuse execute) |
| 9 isolation attestation | GATE_LOCKED; attestation blank |
| 10 unseal execution | BLOCKED |
| 11 decision | BLOCKED |

## Thresholds

```text
MUST NOT MOVE after holdout freeze / SHA freeze
MCID amend only via documented pilot BEFORE unseal
```
