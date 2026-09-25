# Y22 Preregistration — Locked Before Arm Execution

**Protocol:** `Y22-AB-v1`  
**Arms started:** false until Arm A begins  
**Y20/Y21 scorers:** frozen forever (do not reopen)

## Task

Chronological evidence stream with CLAIM / RETRACT / INVALIDATE events.
Answer sealed factual questions; maintain cleaned active claims; drop invalid interim.

## Equal budgets

| Cap | Value |
|-----|-------|
| wall_seconds_max | 14400 |
| token_budget_max | 800000 |
| tool_calls_max | 400 |
| python_subprocess_max | 200 |
| model_pin | identical A/B |
| data | identical `artifacts/y22/public/` sha256 |

## Primary composite (immutable)

```text
0.35 * final_factual_correctness
+ 0.25 * invalidated_claim_cleanup
+ 0.20 * unsupported_claims_score
+ 0.20 * recovery_fidelity
```

MCID for B win: **+0.05** absolute on composite.

## Secondary (cannot override primary)

human_interventions, dispatcher_asks, unsupported narrative claims beyond schema,
failed hypotheses, recovery events, evidence_trace_completeness, cost/wall_time,
premature_stop

## Submission schema

```json
{
  "arm_id": "A|B",
  "final_answers": [{"question_id": "Q00", "value": "EU"}],
  "active_claims": ["F001"],
  "invalidated_claims": ["F010"],
  "dropped_interim": true,
  "decision": "SUPPORTED|REJECTED|INCONCLUSIVE",
  "stop_reason": "string",
  "notes": "string"
}
```

## Integrity

Prefer generator author ≠ arm runners. Record caveat if same lineage.
Do not unseal until both arms frozen.
