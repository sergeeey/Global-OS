# EW1_DECISION — M-EXT2 Chaotic Transient Predictor

**Status:** `INCONCLUSIVE`  
**Protocol:** `EW1-CTP-v1`  
**Exam:** `M-EXT2-EW1`  
**Fidelity:** `SIMULATED_LATTICE_V1`

## Reasons

```text
holdout_class_balance_underpowered
```

## Metrics

```json
{
  "holdout_balance": {
    "n": 150,
    "neg": 0,
    "pos": 150
  },
  "reasons": [
    "holdout_class_balance_underpowered"
  ],
  "verdict": "INCONCLUSIVE"
}
```

## Explicit non-claims

- Not Y19 reopen / not Y19 evidence
- Not Trust Kernel / architecture promote
- Not live physical-system claim (simulated lattice)
- M-EXT1 urllib3 result not used as evidence here
