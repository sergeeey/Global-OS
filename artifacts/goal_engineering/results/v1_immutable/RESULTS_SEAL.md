# GE-STUDY-v1 sealed results

- protocol: `GE-STUDY-v1`
- master_seed: `29072026`
- n_seeds: `20`
- n_trials: `180`
- execution_class: **EXECUTED_DETERMINISTIC**
- live_llm: **NOT_EXECUTED**

## Aggregate oracle_success (mean, 90% CI)

- `S_TRAD`: 0.300 [0.200, 0.400]
- `S_DETAIL`: 0.333 [0.233, 0.433]
- `S_GE`: 1.000 [1.000, 1.000]

## Hypotheses

- `H1_GE_oracle_gt_TRAD`: **CONFIRMED** — S_GE oracle_success > S_TRAD on aggregate under GE-STUDY-v1 behavioral agents
- `H2_GE_oracle_gt_DETAIL`: **CONFIRMED** — S_GE oracle_success > S_DETAIL on aggregate under GE-STUDY-v1
- `H3_GE_false_claim_lt_TRAD`: **CONFIRMED** — S_GE false_claim rate < S_TRAD
- `H4_GE_evidence_gt_baselines`: **CONFIRMED** — S_GE evidence_fidelity > S_TRAD and > S_DETAIL
- `H5_GE_not_free`: **CONFIRMED** — S_GE has higher cost_tokens or latency_ms than S_TRAD (reliability tax)

## Conditional winners (oracle_success)

- `coding`: `S_DETAIL=S_GE`
- `research`: `S_GE`
- `multi_step`: `S_GE`
