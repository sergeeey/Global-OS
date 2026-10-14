# GE-STUDY-v1.1 post-audit appendix

- protocol: `GE-STUDY-v1.1-POST-AUDIT`
- parent_immutable: `GE-STUDY-v1` → `results/v1_immutable/`
- master_seed: `29072026`
- n_seeds: `20`
- n_trials: `240` (4 strategies × 3 tasks × 20 seeds)
- execution_class: **EXECUTED_DETERMINISTIC_POST_AUDIT**
- live_llm: **NOT_EXECUTED**
- causal_status: **NOT_CAUSAL** (mechanism demo only)

## Aggregate oracle_success (mean, 90% CI; within-suite)

- `S_TRAD`: 0.167 [0.083, 0.250]
- `S_DETAIL`: 0.000 [0.000, 0.000]
- `S_DETAIL_VERIFIED`: 0.667 [0.567, 0.767]
- `S_GE`: 0.667 [0.567, 0.767]

## Hypotheses (post-audit labels)

- `H1_GE_oracle_gt_TRAD`: **MECHANISM_SUPPORTED** — S_GE oracle_success > S_TRAD (paired, this suite)
- `H2_GE_oracle_gt_DETAIL_brittle`: **MECHANISM_SUPPORTED** — S_GE oracle_success > brittle S_DETAIL (paired)
- `H2b_GE_oracle_gt_DETAIL_VERIFIED`: **INCONCLUSIVE** — S_GE oracle_success > S_DETAIL_VERIFIED complete runbook (paired)
- `H3_GE_false_claim_lt_TRAD`: **MECHANISM_SUPPORTED** — S_GE false_claim < S_TRAD (paired)
- `H4_GE_evidence_gt_DETAIL_VERIFIED`: **MECHANISM_SUPPORTED** — S_GE evidence_fidelity > S_DETAIL_VERIFIED (paired)
- `H5_GE_not_free_vs_TRAD`: **MECHANISM_SUPPORTED** — S_GE cost or latency > S_TRAD (paired)

## Conditional winners (oracle_success)

- `coding`: `S_TRAD=S_DETAIL=S_DETAIL_VERIFIED=S_GE`
- `research`: `S_DETAIL_VERIFIED=S_GE`
- `multi_step`: `S_DETAIL_VERIFIED=S_GE`

## Fair contrast note

Primary GE-vs-procedure contrast is `S_GE` vs `S_DETAIL_VERIFIED`.
Advantage vs brittle `S_DETAIL` is expected by construction.
