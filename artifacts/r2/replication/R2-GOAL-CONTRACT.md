# R2 Goal Contract — Real scientific replication / audit

**mission_id:** `R2-ATTN-EXPLAIN-REPLICATION-v1`  
**class:** real-use scientific replication (≠ R1 honesty; ≠ synthetic Y-series)  
**external object:** Jain & Wallace (2019), *Attention is not Explanation*, NAACL / arXiv:1902.10186  
**code:** https://github.com/successar/AttentionExplanation (cloned for audit; not authored by GOS)  
**model_pin:** composer-cloud-agent-bundle  
**ADR-0009:** no new T0/T1 surfaces

## Product / research thesis (context, not claim of proof)

> Global OS does not yet look like a raw-intelligence amplifier. It looks like an
> OS for long, checkable work by a strong intellect: durable goals, state,
> negative-result retention, provenance, failure→continue, terminal without
> human dispatcher.

R2 tests whether that operational pattern transfers to an **external** scientific object.

## Objective (given once)

Independently assess the paper’s main claim:

> Standard attention weights largely do **not** provide meaningful explanations
> of model predictions (weak alignment with gradient/feature-importance measures;
> alternate attention distributions can yield equivalent predictions).

Deliver:
1. Reproduction / audit of released evidence (CorrStats / evaluate artifacts)
2. Robustness notes (scope, env limits, what could not be re-trained)
3. ≥1 substantive extension (independent computational probe of a core mechanism)
4. Terminal scientific decision: `SUPPORTED` | `PARTIAL` | `FAILED` | `INCONCLUSIVE`
5. Reproducible report under `artifacts/r2/replication/`

## Invariants

- Do not invent paper numbers, tables, or citations
- Do not retune Y20–Y22 scorers; no Y23
- Do not treat R1 self-score as comparative GOS advantage
- Executor **must not** write the independent review scores
- Checkpoint ≠ stop; failure → minimal fix → regression → continue
- Official full retrain may be `BLOCKED_ENVIRONMENT` — must be explicit, not silent skip

## Stop

When SUBMISSION.json + REPORT.md exist with terminal decision **and** independent
reviewer has written `review/INDEPENDENT_REVIEW.md` from locked rubric only.

## Non-goals

M1.5 · Continual SI · universal GOS advantage · CRM/Docker operational work
