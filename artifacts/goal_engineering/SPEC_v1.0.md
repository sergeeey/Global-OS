# Goal Engineering Specification v1.0

**Status:** Normative for construct definition; **empirical claims scoped** to GE-STUDY-v1  
**Date:** 2026-10-14  
**Basis:** Confirmed hypotheses under `EXECUTED_DETERMINISTIC` + literature priors explicitly marked as non-proof  
**Non-basis:** Live LLM trials (not executed); marketing; model confidence

```text
implemented approximation ≠ fulfilled contract
CONFIRMED under behavioral agents ≠ proven for production LLMs
```

## 1. Definition

**Goal Engineering (GE)** is a tasking methodology that binds an autonomous agent to:

1. an **immutable GoalContract** (versioned objective + constraints),  
2. a machine-interpretable **Definition of Done** (DoD) — observable success criteria,  
3. an **EvidenceLedger** — scope-matched, latest-state records that gate SUCCESS,

such that completion is **fail-closed** without evidence, and agent self-assessment alone is never sufficient.

## 2. What v1.0 claims (confirmed in-repo)

Under GE-STUDY-v1 deterministic behavioral agents (180 trials):

| Claim ID | Claim | Scope |
|----------|-------|-------|
| C1 | GE raises oracle_success vs vague traditional prompts | aggregate, this suite |
| C2 | GE raises oracle_success vs brittle detailed instructions | aggregate; driven by research + multi_step |
| C3 | GE reduces false_claim vs traditional prompts | aggregate |
| C4 | GE yields higher evidence_fidelity than TRAD and DETAIL | aggregate |
| C5 | GE incurs higher token cost and/or latency vs TRAD | reliability tax |
| C6 | On simple coding with complete steps, GE ties DETAIL on success | conditional |

**Not claimed:** universal superiority; live-LLM generalization; superiority vs well-maintained SOPs that already encode verify/retraction; production readiness.

## 3. When to use GE (from conditional evidence)

| Situation | Recommendation |
|-----------|----------------|
| Outcome ambiguity / “done?” disputes | **Use GE** |
| Retractions, contradictions, contested facts | **Use GE** |
| Multi-phase side effects (publish/deploy) | **Use GE** (verify-before-effect) |
| High cost of false success | **Use GE** even if slower |
| Simple, stable coding with a complete tested runbook | DETAIL acceptable for outcome; prefer GE if audit/evidence required |
| Authoring budget tiny and task disposable | TRAD may be enough — accept false-claim risk |

## 4. Contract schema (normative minimal)

Compatible with `contracts/schemas/goal_contract.schema.json` (extend, do not fork silently):

```json
{
  "goal_id": "goal_<id>",
  "version": 1,
  "objective": { "text": "<observable outcome>" },
  "success_criteria": [
    { "id": "sc_01", "description": "<checkable statement>" }
  ],
  "non_goals": ["<explicit exclusions>"],
  "forbidden_outcomes": ["<must not happen>"],
  "evidence_requirements": {
    "sc_01": { "verification_tier": 2 }
  }
}
```

### Definition of Done rules

- Every `success_criteria[]` item is **observable** (world state, command exit, receipt).  
- “Looks good” / “model is confident” is **not** a criterion.  
- Changing DoD requires a new `version` (GOS-I06).

### EvidenceLedger entry (normative shape)

```json
{
  "criterion_id": "sc_01",
  "kind": "command_output|code_diff|citation|verify_receipt|publish_receipt|file_hash|event_log",
  "value": "<payload>",
  "observed_at": "<iso8601>",
  "scope": "<path|source|phase>",
  "verifier": "<tool_or_oracle_id>"
}
```

**Gate:** `SUCCESS` iff ∀ criteria ∃ ledger entry that an **independent** checker accepts.  
Missing evidence → `BLOCKED` or continue — never assertion SUCCESS (C3).

## 5. Anti-patterns (forbidden)

| Anti-pattern | Why |
|--------------|-----|
| LLM boolean “is it done?” as sole gate | GOS-I10 / false confidence |
| Regex-only nested JSON as contract validation | brittle; not semantic proof |
| Silent fallback to allow on verify error | fail-open destroys C3 |
| Mutating goal in place | GOS-I06 |
| Treating URL/SHA presence as truth | GOS-I08 |
| Same agent certifies its own SUCCESS without oracle/tool | GOS-I10 |
| Marking PRODUCTION_PROVEN from this study alone | fidelity limit |

## 6. Metrics for any GE deployment

Must report at least:

1. oracle / machine-verified success  
2. false_claim rate  
3. evidence_fidelity  
4. cost (tokens or $)  
5. latency  
6. autonomy / interventions  

CI or uncertainty required for comparative claims.

## 7. Relationship to alternatives

```text
S_TRAD   = underspecified outcome + assertion stop
S_DETAIL = procedural plan (planning harness lever)
S_GE     = outcome contract + evidence release control
```

Literature prior: planning and verification are **different levers** (harness study).  
v1.0 engineering rule: **prefer GE for release control**; use DETAIL as optional *strategy scaffold inside* GE, not as a substitute for DoD+Ledger.

## 8. Versioning

- **GE Spec 1.0** — this document  
- Empirical appendix: `GE-STUDY-v1` deterministic seal  
- Next appendices (not part of 1.0 claims): `GE-STUDY-v1-LIVE` when PROTOCOL §7 is executed and sealed

## 9. Honesty footer

Confirmed results support GE as a **reliability and evidence-quality methodology** with a measurable cost tax in the tested behavioral suite — especially under incomplete procedures and multi-step side effects. They do **not** prove GE is always the best tasking strategy for every coding runbook or every live model.
