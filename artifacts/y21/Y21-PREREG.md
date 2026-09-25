# Y21 Preregistration — Locked Before Arm Execution

**Protocol version:** `Y21-AB-v1`  
**Plan agree SHA:** `59e0be5`  
**Prereg boundary SHA:** set in `CURRENT_STATE.json` at lock commit  
**Arms started:** false until Arm A begins

## Task

Hidden deterministic Mealy machine (4 states, alphabets {0,1,2}).  
Public: train I/O traces. Predict: sealed holdout outputs given inputs only.

## Equal budgets (immutable)

| Cap | Value |
|-----|-------|
| model_pin | identical across A/B (recorded at arm start) |
| wall_seconds_max | 14400 |
| token_budget_max | 800000 |
| tool_calls_max | 400 |
| python_subprocess_max | 200 |
| tools | filesystem + python |
| data | identical `artifacts/y21/public/` sha256 |

## Primary metric (immutable)

- Name: `sealed_exact_match_rate`
- MCID for B win: **+0.05 absolute** vs A
- Secondary metrics cannot rescue a primary loss

## Secondary metrics

human_interventions, unsupported_claims, dispatcher_asks, failed_hypotheses,
recovery/state_loss, evidence_trace_completeness, cost/wall_time, premature_stop

## Submission schema

```json
{
  "arm_id": "A|B",
  "predicted_outputs": [{"trace_id": "S000", "output": [0,1,2]}],
  "claimed_n_states": 4,
  "decision": "SUPPORTED|REJECTED|INCONCLUSIVE",
  "stop_reason": "string",
  "notes": "string"
}
```

## Competing architecture hypotheses

| ID | Statement |
|----|-----------|
| H_gos_primary | B wins sealed_exact_match_rate by MCID under equal caps |
| H_model_alone | A matches/beats B on primary; GOS adds process/cost only |
| H_inconclusive | Within MCID |

## Explicit non-goals

Running arms before lock · Ablation C · Y20 mutation · LH/M1.5
