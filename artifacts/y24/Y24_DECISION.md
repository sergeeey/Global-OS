# Y24_DECISION — Adaptive Verifier Complexity Threshold

**Status:** `REJECT`  
**Generated (UTC):** 2026-09-30T20:35:19.637061+00:00  
**Experiment SHA:** `1ce7569695c32975968f62b47c057784d3828781`  
**Fold:** `fold2_enlarged_holdout`  
**Fidelity:** `HEURISTIC_HARNESS_v1`  
**H_memory:** `INCONCLUSIVE`

## Reasons

```text
no_stratum_met_keep_gates
```

## Stratum snapshot

```json
{
  "HIGH": {
    "A": {
      "false_block_rate": 0.0,
      "material_escape_rate": 0.0,
      "n": 10,
      "task_completion_rate": 1.0,
      "verification_cost_mean": 200.05
    },
    "B": {
      "false_block_rate": 0.0,
      "material_escape_rate": 0.0,
      "n": 10,
      "task_completion_rate": 1.0,
      "verification_cost_mean": 1050.4
    },
    "C": {
      "false_block_rate": 0.0,
      "material_escape_rate": 0.0,
      "n": 10,
      "task_completion_rate": 1.0,
      "verification_cost_mean": 1150.4
    }
  },
  "LOW": {
    "A": {
      "false_block_rate": 0.0,
      "material_escape_rate": 0.0,
      "n": 9,
      "task_completion_rate": 1.0,
      "verification_cost_mean": 200.05
    },
    "B": {
      "false_block_rate": 0.1111111111111111,
      "material_escape_rate": 0.0,
      "n": 9,
      "task_completion_rate": 1.0,
      "verification_cost_mean": 1055.9555555555555
    },
    "C": {
      "false_block_rate": 0.0,
      "material_escape_rate": 0.0,
      "n": 9,
      "task_completion_rate": 1.0,
      "verification_cost_mean": 1150.4
    }
  },
  "MEDIUM": {
    "A": {
      "false_block_rate": 0.0,
      "material_escape_rate": 0.0,
      "n": 10,
      "task_completion_rate": 1.0,
      "verification_cost_mean": 200.05
    },
    "B": {
      "false_block_rate": 0.3,
      "material_escape_rate": 0.0,
      "n": 10,
      "task_completion_rate": 1.0,
      "verification_cost_mean": 1065.4
    },
    "C": {
      "false_block_rate": 0.0,
      "material_escape_rate": 0.0,
      "n": 10,
      "task_completion_rate": 1.0,
      "verification_cost_mean": 1150.4
    }
  }
}
```

## Explicit non-claims

- Not Trust Kernel promotion
- Not T3 evidence
- Not production security
- Heuristic harness ≠ live-LLM verification claim

## Note

Arms A/B/C executed as prereg-shaped heuristic verifiers with full cost ledger; not Trust Kernel; not live-LLM claim unless fidelity upgraded.
