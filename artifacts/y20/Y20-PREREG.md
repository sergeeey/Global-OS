# Y20 Preregistration — Locked Before Arm Execution

**Protocol version:** `Y20-AB-v1`  
**Preregistration boundary SHA:** `278c10d` (immutable)  
**Locked at:** `278c10d`  
**Arms started:** **false** (do not change metrics/scorer/generator/budgets after arm start)

## Competing process hypotheses (architecture)

| ID | Statement |
|----|-----------|
| H_gos_helps | Same model under Global OS yields better process profile (fewer unsupported claims / interventions / better evidence+stop) and/or better sealed science metrics under equal budget |
| H_model_alone | Strong agent without GOS matches science metrics; GOS adds cost without process gain |
| H_inconclusive | Under equal budget, differences are within noise / underpowered |

Scientific task outcome (`SUPPORTED`/`REJECTED`/`INCONCLUSIVE` on causal recovery) is
**per-arm** and separate from architecture comparison.

## Task class

Synthetic statistical-causal system:

- `N_VARS = 20` continuous variables
- Hidden DAG with confounders, mediators, nonlinear links, spurious correlations
- Observational sample for agents; sealed interventional environments for scoring
- Agents must not receive generator master seed, DAG, or true `do()` expectations

## Equal budget (immutable after lock)

| Cap | Value |
|-----|-------|
| `model_pin` | same strong agent model for A and B (operator-recorded at arm start) |
| `wall_seconds_max` | 14400 (4h) per arm |
| `token_budget_max` | 800000 per arm |
| `tool_calls_max` | 400 per arm |
| `python_subprocess_max` | 200 per arm |
| Tool surface | filesystem + python interpreter only |
| Data | identical `public/` pack (sha256 locked) |

Losing arm must **not** receive extra compute.

## Primary metrics (preregistered)

### Scientific (blind scorer)

1. **Edge precision / recall** on claimed directed edges vs sealed scoring edge set
2. **Interventional MAE** on sealed `do(X=x)` targets (mean abs error vs true E[Y|do])
3. **Claimed-subgraph reproducibility** — claimed edges must be listed explicitly in submission

### Process (operator log + arm `process_log.json`)

4. Human interventions count  
5. Dispatcher-asks count  
6. Hypotheses tried  
7. Failed experiments  
8. Unsupported conclusions count  
9. State-loss incidents / recovery events  
10. Evidence-trace completeness (0–1 checklist)  
11. Premature stop (bool) + stop correctness  
12. Tool/compute cost + wall time (must be ≤ caps)

Schema: `artifacts/y20/process_log.schema.json` · Sequence: `Y20-EXECUTION-PROTOCOL.md`

## Submission schema (both arms)

JSON file `submission.json`:

```json
{
  "arm_id": "A|B",
  "claimed_edges": [["Xi","Xj"], ...],
  "intervention_predictions": [
    {"intervention_id": "I1", "target": "Y", "predicted_mean": 0.0}
  ],
  "decision": "SUPPORTED|REJECTED|INCONCLUSIVE",
  "stop_reason": "string",
  "notes": "string"
}
```

## Scoring

`global_os.evals.research.y20_causal_ab.score_submission` against sealed pack.
Blind: write raw metrics before unblinding arm identity in the comparison report.

## Explicit non-goals of this prereg stage

- Running Arm A or Arm B
- Ablation C
- Y21/Y22
- LH / M1.5 / Continual SI

## FUTURE (not Y20)

Arm C = strong agent + durable checkpoint only (ablation).
