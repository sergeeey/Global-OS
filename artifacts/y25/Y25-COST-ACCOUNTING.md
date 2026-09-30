# Y25 — Cost accounting (LOCKED)

**Status:** `COST_ACCOUNTING_LOCKED`  
**Protocol:** `Y25-MV-v1`

## Formula

```text
pair_cost =
  1.0  * llm_cost_tokens
+ 50.0 * tool_calls
+ 5000 * human_interventions
+ 0.001 * latency_ms
+ 100.0 * verification_calls
+ 10.0 * recovery_overhead_seconds
+ 1.0  * time_to_diagnosis_s
```

Aligned with Y24 weights where overlapping; adds `time_to_diagnosis_s` at weight 1.0
because diagnosis latency is first-class for memory value.

## Parity

W0 and W1 share identical budgets and ledger schema. Cost wins via unaccounted
compute → REJECT / invalid run.
