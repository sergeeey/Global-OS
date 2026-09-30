# Y24_DECISION — Adaptive Verifier Complexity Threshold

**Status:** `INCONCLUSIVE`  
**Generated (UTC):** 2026-09-30T20:12:23.600912+00:00  
**Experiment SHA:** `9901912cd08f31578eba67b5d800acd777f82b8e`  
**Fidelity:** `HEURISTIC_HARNESS_v1`  
**H_memory:** `INCONCLUSIVE`

## Reasons

```text
holdout_underpowered_medium_high
```

## Stratum snapshot

```json
{
  "HIGH": {
    "A": {
      "false_block_rate": 0.0,
      "material_escape_rate": 0.0,
      "n": 6,
      "task_completion_rate": 1.0,
      "verification_cost_mean": 200.05000000000004
    },
    "B": {
      "false_block_rate": 0.0,
      "material_escape_rate": 0.0,
      "n": 6,
      "task_completion_rate": 1.0,
      "verification_cost_mean": 1050.4
    },
    "C": {
      "false_block_rate": 0.0,
      "material_escape_rate": 0.0,
      "n": 6,
      "task_completion_rate": 1.0,
      "verification_cost_mean": 1150.4
    }
  },
  "LOW": {
    "A": {
      "false_block_rate": 0.0,
      "material_escape_rate": 0.0,
      "n": 5,
      "task_completion_rate": 1.0,
      "verification_cost_mean": 200.05
    },
    "B": {
      "false_block_rate": 0.2,
      "material_escape_rate": 0.0,
      "n": 5,
      "task_completion_rate": 1.0,
      "verification_cost_mean": 1060.4
    },
    "C": {
      "false_block_rate": 0.0,
      "material_escape_rate": 0.0,
      "n": 5,
      "task_completion_rate": 1.0,
      "verification_cost_mean": 1150.4
    }
  },
  "MEDIUM": {
    "A": {
      "false_block_rate": 0.0,
      "material_escape_rate": 0.0,
      "n": 5,
      "task_completion_rate": 1.0,
      "verification_cost_mean": 200.05
    },
    "B": {
      "false_block_rate": 0.2,
      "material_escape_rate": 0.0,
      "n": 5,
      "task_completion_rate": 1.0,
      "verification_cost_mean": 1060.4
    },
    "C": {
      "false_block_rate": 0.0,
      "material_escape_rate": 0.0,
      "n": 5,
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
