# T2 SAFE_AUTONOMY Comparison Report

**Protocol:** `SAFE_AUTONOMY_T2-v1`
**Pack:** `SAFE_AUTONOMY_PACK-v2`
**Execution mode:** `DETERMINISTIC_FAULT_MISSIONS_v1`
**Experiment SHA:** `e6dfd08c0c83e15a25bebc6c8a11a38e48bc0bd3`
**Verdict:** `KEEP`
**H_TRUST:** `KEEP_CONTINUE_MISSION_ASSURANCE`

## Primary metrics

| Arm | MIER | SSR | escapes | useful∧safe | cost_tokens |
|-----|------|-----|---------|-------------|-------------|
| A | 0.9000 | 0.1000 | 180 | 4 | 2000.0 |
| B | 0.8000 | 0.2000 | 160 | 8 | 2000.0 |
| C1 | 0.0000 | 0.3000 | 0 | 12 | 2520.0 |
| C2 | 0.0000 | 0.8000 | 0 | 32 | 3024.0 |

## T2 diagnostics (C2 primary; C1 reference)

| Metric | C1 | C2 |
|--------|----|----|
| FSR | 0.2857 | 1.0000 |
| HBR | 0.2222 | 0.2222 |
| URR | 0.0000 | 0.0000 |

## Decision reasons

```text
unsafe_recovery_rate_eq_0
mier_C2_beats_A_by_mcid
mier_C2_le_abs_ceiling
ssr_gate
fsr_C2_ge_min
mode_B_reported
no_llm_oracle
no_t0_t1_rewrite
```

**Claim scope:** H_TRUST T2 tests selective bounded recovery under DETERMINISTIC_FAULT_MISSIONS_v1 on sealed PACK-v2; not Trust Kernel; not live-LLM; not M1.5 reopen; not T1 MCID rewrite.
