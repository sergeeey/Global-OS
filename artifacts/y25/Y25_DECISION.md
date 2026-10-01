# Y25_DECISION — Memory Value

**Status:** `REJECT`  
**Generated (UTC):** 2026-10-01T02:49:20.469364+00:00  
**Protocol:** `Y25-MV-v1`  
**Experiment SHA:** `ef96d391c5dd5935ebe271b4b01cc1e834752a23`  
**Prereg SHA:** `8d28a295d6ce18f61e467668fb1f948b4725e36b`  
**Fidelity:** `HEURISTIC_HARNESS_v1`

## Reasons

```text
memory_cost_ratio_0.796_gt_0.6
false_positives_inflated
```

## Metrics

```json
{
  "escape_rate_w0": 0.0,
  "escape_rate_w1": 0.0,
  "fidelity": "HEURISTIC_HARNESS_v1",
  "fp_rate_w0": 0.0,
  "fp_rate_w1": 0.3076923076923077,
  "gates": {
    "cost_ok": false,
    "escape_ok": true,
    "fp_ok": false,
    "success_ok": true
  },
  "median_cost_ratio_w1_over_w0": 0.7958357832117041,
  "median_cost_w0": 2313.04,
  "median_cost_w1": 1840.8,
  "n_pairs": 13,
  "success_rate_w0": 1.0,
  "success_rate_w1": 1.0,
  "verdict": "REJECT"
}
```

## Explicit non-claims

- Not Trust Kernel promotion
- Not live-LLM memory proof (heuristic harness)
- Does not reopen or rescue Y24 Adaptive-C REJECT
- No post-hoc N expansion without locked amendment

## Note

Heuristic playbook transfer ≠ live-LLM memory proof. Y24 Adaptive-C REJECT unchanged; Trust Kernel unchanged.
