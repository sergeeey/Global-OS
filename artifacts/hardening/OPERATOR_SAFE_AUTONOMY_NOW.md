# OPERATOR — after T1 REJECT

M1.5 closed. Benchmark frozen. T1 A/B/C **complete**. Verdict: **REJECT**.

## Provenance

```text
EXAM_SHA     = 7ab345e5badb00a8c97ffdb7010ee4eb42dac4bb
AUDIT_SHA    = a7960d9616c9c08224f5be9e1e7097bca9744bd0
BENCHMARK    = SAFE_AUTONOMY_BENCHMARK-v1
MCID         = SET_BY_VARIANCE_PILOT_v1 (mier=0.04 / ssr=0.18 / eps=0.02)
T1_MODE      = DETERMINISTIC_FAULT_MISSIONS_v1
T1_VERDICT   = REJECT (verifier_tax_2_0_completion)
DECISION     = artifacts/safe_autonomy_t1/T1_DECISION.md
ADR          = docs/adr/ADR-0011-t1-mission-assurance-reject.md
```

## Primary numbers

| Arm | MIER | SSR |
|-----|------|-----|
| A | 0.90 | 0.10 |
| B | 0.80 | 0.20 |
| C | 0.00 | 0.30 |

Integrity escapes fell; completion utility tax failed frozen KEEP.

## Do NOT

- promote Mission Assurance / Trust Kernel
- rewrite MCID
- re-run 48h
- Y23 / IQ-rescue
- claim H_TRUST confirmed

## Next

Post-T1 replan from evidence (overblocking). New experiment requires new prereg.
