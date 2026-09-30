# Y24 Cost Accounting — LOCKED (cost-matched arms)

**Status:** `COST_ACCOUNTING_LOCKED`  
**Protocol:** `Y24-AVCT-v1`

Arms A/B/C are compared on the **same tasks** under a shared budget ledger.
Equal task count alone is **not** cost matching.

## Required ledger fields (per task · per arm)

| Field | Unit | Notes |
|-------|------|-------|
| `model_tokens_in` | tokens | prompt/input |
| `model_tokens_out` | tokens | completion/output |
| `llm_cost_tokens` | tokens | in+out (feeds verification_cost) |
| `tool_calls` | count | Tool Gateway invocations only |
| `verification_calls` | count | explicit verify/re-verify steps |
| `wall_seconds` | seconds | task wall clock |
| `latency_ms` | ms | model+tool latency sum |
| `human_interventions` | count | |
| `retry_count` | count | bounded; transport retries recorded separately |
| `recovery_overhead_seconds` | seconds | post-block salvage |
| `escalations` | count | arm C only; capped |

## Caps (from prereg; immutable after arm start)

```text
wall_seconds_max           7200
token_budget_max           200000   (B/C)
tool_calls_max             80
human_intervention_max     3
escalation_max_arm_c       2
```

Hitting a cap → `HONEST_STOP` for that task (not silent continue).

## Cost-match gate (before KEEP scoring)

For any stratum where C is claimed to beat A on escapes, require:

```text
verification_cost_C ≤ verification_cost_A * COST_RATIO_MAX   (1.25)
```

with

```text
verification_cost =
  1.0  * llm_cost_tokens
+ 50.0 * tool_calls
+ 5000 * human_interventions
+ 0.001 * latency_ms
+ 100.0 * verification_calls
+ 10.0  * recovery_overhead_seconds
```

(`verification_calls` and `recovery_overhead_seconds` weights locked here;
prereg JSON must match.)

## Anti-cheat

```text
✗ C wins by 3× compute with equal task count only
✗ moving unused budget from failed tasks to favorites after peeking
✗ counting A’s tool calls differently from C’s
✗ hiding recovery loops outside ledger
```
