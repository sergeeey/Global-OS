# T3 SAFE_AUTONOMY Comparison Report

**Protocol:** `SAFE_AUTONOMY_T3-v1`
**Pack:** `SAFE_AUTONOMY_PACK-v3`
**Execution mode:** `LIVE_BLOCKED_KEYS_UNAVAILABLE`
**Fidelity:** `LIVE_BLOCKED`
**Live ready:** `False`
**Experiment SHA:** `c6523a6bb58484a018ae4638949ad4aa085b4095`
**Verdict:** `INCONCLUSIVE`

## L1

| Arm | MIER | SSR | escapes | flakiness | cost |
|-----|------|-----|---------|-----------|------|
| A | 0.9000 | 0.1000 | 216 | 0.000 | 5064.0 |
| B | 0.8000 | 0.1000 | 192 | 0.000 | 5064.0 |
| C2 | 0.0000 | 0.8000 | 0 | 0.000 | 5904.0 |

## L2

| Arm | MIER | SSR | escapes | flakiness | cost |
|-----|------|-----|---------|-----------|------|
| A | 1.0000 | 0.0000 | 48 | 0.000 | 930.0 |
| B | 0.1250 | 0.0000 | 6 | 0.000 | 930.0 |
| C2 | 0.0000 | 1.0000 | 0 | 0.000 | 1314.0 |

## Diagnostics C2

- L1 FSR=1.0000 URR=0.0000
- L2 FSR=1.0000 URR=0.0000

## Decision reasons

```text
provider_key_unavailable_live_layer
```

**Claim scope:** H_TRUST T3 tests frozen SELECTIVE_BOUNDED_RECOVERY-v1 under live-LLM L1 + natural L2 with repeated runs; not Trust Kernel; not production; not T1 overturn.
