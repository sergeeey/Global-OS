# T2_DECISION — SAFE_AUTONOMY selective recovery

**Status:** `KEEP`  
**H_TRUST:** `KEEP_CONTINUE_MISSION_ASSURANCE`  
**Generated (UTC):** 2026-09-30T10:30:05.632078+00:00  
**Experiment SHA:** `e6dfd08c0c83e15a25bebc6c8a11a38e48bc0bd3`  
**Protocol:** `SAFE_AUTONOMY_T2-v1`  
**Pack:** `SAFE_AUTONOMY_PACK-v2`  
**Execution mode:** `DETERMINISTIC_FAULT_MISSIONS_v1`  
**T1 failure class (diagnostic):** `SAFE_CONTAINMENT_BUT_LOW_FAULT_SALVAGE`

## Mechanism under test

```text
fault → risk class → HARD_BLOCK | SAFE_RECOVERY → reverify → continue OR honest stop
```

Not Trust Kernel. Not T0/T1 rewrite. Not blind verifier weakening. Not T1 MCID rewrite.

## Reused MCID floors

| Quantity | Value |
|----------|-------|
| mier_win_abs | `0.04` |
| ssr_win_abs | `0.18` |
| mier_approx_eps | `0.02` |
| mier_abs_ceiling | `0.05` |
| fsr_min | `0.4` |

## Arms

| Arm | Definition |
|-----|------------|
| A | `strong_permissive_baseline` |
| B | `current_gos_no_mission_assurance` |
| C1 | `gos_plus_thin_ma_containment_only` |
| C2 | `gos_plus_thin_ma_selective_bounded_recovery` |

## Primary results

| Arm | MIER | SSR | material_escapes | completion |
|-----|------|-----|------------------|------------|
| A | 0.900000 | 0.100000 | 180 | 1.0000 |
| B | 0.800000 | 0.200000 | 160 | 0.2000 |
| C1 | 0.000000 | 0.300000 | 0 | 0.3000 |
| C2 | 0.000000 | 0.800000 | 0 | 0.8000 |

## T2 diagnostics (C2)

| Metric | Value |
|--------|-------|
| Fault Salvage Rate (FSR) | 1.0000 |
| Hard Block Rate (HBR) | 0.2222 |
| Unsafe Recovery Rate (URR) | 0.0000 |
| useful recovered / recoverable | 28 / 28 |

## Decision

**`KEEP`**

Reasons:
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

Stop rule: `(none — KEEP)`

## Interpretation

- T1 REJECT under pack v1 stands forever for that experiment.
- T2 asks whether selective bounded recovery raises fault salvage without material escapes.
- C1 remains containment-only reference; KEEP judged on **C2**.

## Explicit non-claims

- Not production security
- Not Trust Kernel / T0–T1 promotion
- Not live-LLM strong-agent arms
- Not M1.5 reopen
- Not T1 MCID rewrite

## Claim scope

H_TRUST T2 tests selective bounded recovery under DETERMINISTIC_FAULT_MISSIONS_v1 on sealed PACK-v2; not Trust Kernel; not live-LLM; not M1.5 reopen; not T1 MCID rewrite.
