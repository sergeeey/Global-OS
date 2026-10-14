# Falsifiable Hypotheses — GE-STUDY-v1

> **Audit:** v1 seal labels `CONFIRMED` are superseded — see `POST_HOC_AUDIT.md`.  
> Post-audit runner emits `MECHANISM_*` / `INCONCLUSIVE` only (`causal_status=NOT_CAUSAL`).  
> Fair procedural contrast is **H2b** vs `S_DETAIL_VERIFIED` (v1.1 appendix).

Preregistered before sealing `artifacts/goal_engineering/results/v1_immutable/`.  
Decision rule: 90% **paired** bootstrap CI on mean difference; seeds via FNV-1a (not `hash()`).

## Strategies (independent variable)

| ID | Name | Tasking form |
|----|------|----------------|
| `S_TRAD` | Traditional prompt | Vague “do your best”; assertion-based completion |
| `S_DETAIL` | Detailed instructions | Ordered procedural steps; success after steps |
| `S_GE` | Goal Engineering | Immutable GoalContract + DoD criteria + EvidenceLedger gate |

## Primary outcome

`oracle_success` — independent evaluator against hidden oracle (not agent claim).

## Secondary outcomes

- `false_claim` — claimed success ∧ ¬oracle_success  
- `evidence_fidelity` — ledger entries match oracle reality  
- `autonomy` — 1 − human_interventions/budget  
- `cost_tokens`, `latency_ms`, `steps`

## Hypotheses

### H1 — GE beats traditional on oracle success (aggregate)

**H1₀:** mean(oracle_success | S_GE) ≤ mean(oracle_success | S_TRAD)  
**H1₁:** mean(oracle_success | S_GE) > mean(oracle_success | S_TRAD)  
**Confirm if:** CI90 for (GE − TRAD) lies entirely above 0.

### H2 — GE beats detailed instructions on oracle success (aggregate)

**H2₀:** mean(oracle_success | S_GE) ≤ mean(oracle_success | S_DETAIL)  
**H2₁:** mean(oracle_success | S_GE) > mean(oracle_success | S_DETAIL)  
**Confirm if:** CI90 for (GE − DETAIL) lies entirely above 0.

*Note:* H2 can fail even if H1 holds — complete runbooks may match GE on simple coding.

### H3 — GE reduces false completion claims vs traditional

**H3₀:** mean(false_claim | S_GE) ≥ mean(false_claim | S_TRAD)  
**H3₁:** mean(false_claim | S_GE) < mean(false_claim | S_TRAD)  
**Confirm if:** CI90 for (GE − TRAD) on false_claim lies entirely below 0.

### H4 — GE improves evidence fidelity vs both baselines

**H4₀:** evidence_fidelity(GE) is not greater than both baselines  
**H4₁:** evidence_fidelity(GE) > TRAD and > DETAIL (both contrasts CI > 0)

### H5 — GE is not free (reliability tax)

**H5₀:** cost_tokens and latency_ms of GE are not higher than TRAD  
**H5₁:** at least one of cost_tokens or latency_ms has (GE − TRAD) CI entirely above 0

### H6 — Conditional (qualitative, pre-registered)

| Condition | Predicted best on oracle_success | Rationale |
|-----------|----------------------------------|-----------|
| Simple coding + complete steps | S_DETAIL ≈ S_GE | Procedure covers oracle |
| Research with retractions omitted from steps | S_GE ≫ S_DETAIL, S_TRAD | DoD forces retraction handling |
| Multi-step with verify omitted from steps | S_GE ≫ S_DETAIL; S_TRAD mixed | Evidence gate blocks publish-without-verify |
| High liability / false-pass cost | Prefer S_GE even if slower | Harness verifier literature |

H6 is scored via `conditional_winners_oracle_success`, not a single CI.

## Fidelity classes

| Class | Role |
|-------|------|
| `EXECUTED_DETERMINISTIC` | Behavioral agents in-repo — **may** confirm/reject H1–H5 for that class only |
| `PROTOCOL_ONLY_NOT_EXECUTED` | Live LLM / multi-provider — must not inherit deterministic verdicts |

## Forbidden overclaim

```text
H* CONFIRMED under EXECUTED_DETERMINISTIC
  ≠  GE proven for production LLM agents
  ≠  GE always beats a well-maintained runbook
```
