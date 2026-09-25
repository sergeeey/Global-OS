# R2 REPORT — Attention is not Explanation (replication/audit)

**Mission:** R2-ATTN-EXPLAIN-REPLICATION-v1  
**Target:** Jain & Wallace, arXiv:1902.10186  
**Executor decision (proposal):** `PARTIAL`  
**Review rubric lock:** `9bd0df5` / 2026-09-25T17:05:00Z  
**Independent review:** `review/` (separate contour; executor does not self-certify usefulness)

## Method

1. Paper PDF + upstream code observe  
2. Aggregate released `CorrStats_kendalltau` (ag/al/gl)  
3. Official retrain attempt status → BLOCKED_ENVIRONMENT  
4. Extension: train tiny BiGRU+attention on synthetic token-presence; counterfactual attention  
5. Failure→fix: untrained probe was prediction-collapsed; retrained probe used instead  

## Results

### CorrStats audit
- n_configs=88
- median ag=0.314; median gl=0.499
- frac(ag<0.5)=0.736; frac(ag<gl)=0.667

### Extension probe
- eval_acc=1.000; pred_hist=[37, 27]
- same@permuted_attn=0.625
- same@random_attn=0.578
- mean logit L2 under perm=7.526

## Executor terminal

**PARTIAL** — Released CorrStats support weak attn–gradient alignment across many configs; trained tiny-model probe shows non-trivial prediction-preserving attention changes. Full official retrain blocked.

## Non-claims
No GOS advantage · No M1.5 · No Continual SI · Not full SST/IMDB retrain
