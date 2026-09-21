# SPEC.md — Technical Specification v0.1

**Project:** Global OS (ex Goal OS)  
**Date:** 2026-09-21  
**Status:** M0 Trustworthy Skeleton (in progress) — not claimed DoD v0.1 complete  

## Mission

Maximize useful autonomous work per unit of unverified human trust — not tool-call count, not agent count, not zero human involvement at any cost.

## Formula

$$
\text{GlobalOS} =
\text{GoalContract} +
\text{EpistemicKernel} +
\text{DurableRuntime} +
\text{AuthorityKernel} +
\text{DynamicCognitiveOrganization} +
\text{EnvironmentCompiler} +
\text{WorldInteraction} +
\text{VerificationFabric} +
\text{AdaptiveLearning}
$$

LLM is interchangeable compute behind adapters.

## Honesty rule

$$
\text{implemented approximation} \neq \text{fulfilled contract}
$$

Capability states: `CONTRACTED` | `STUBBED` | `STATICALLY_IMPLEMENTED` | `RUNTIME_VERIFIED_*` | `PRODUCTION_PROVEN`.  
See `docs/capability_matrix.json` and generated `docs/IMPLEMENTATION_STATUS.md`.

## Contracts-first rule

Every core entity has: schema, version, ID semantics, state transitions, validation, events, ownership, tests, migration policy.

Sequence: Problem → Contract → Invariant → Tests → Implementation → Runtime evidence.

## Core entities

| Entity | State | Notes |
|--------|-------|-------|
| GoalContract | RUNTIME_VERIFIED_LOCAL | Immutable versions; amendments only |
| Event | RUNTIME_VERIFIED_LOCAL | Append-only; SQLite adapter |
| ActionProposal / EffectReceipt | RUNTIME_VERIFIED_LOCAL | Authority + gateway |
| Evidence / Claim | RUNTIME_VERIFIED_LOCAL | Invalidation seed |
| Observation / Belief / Commitment | RUNTIME_VERIFIED_LOCAL | Obs/Belief store + Commitment NEEDS_REVIEW on invalidation |
| OrgUnit | RUNTIME_VERIFIED_LOCAL | manager_workers compiler |
| MissionContract | RUNTIME_VERIFIED_LOCAL | Outcome assigner; rejects microsteps |
| ExecutionEnvironment | RUNTIME_VERIFIED_LOCAL | EnvironmentCompiler + ChangeGate lifecycle |
| Epistemic Model / Forecast / Decision | RUNTIME_VERIFIED_LOCAL | Invalidation chain GOS-I12 |
| ReasoningBudget / ContextManifest / ClarificationPolicy | RUNTIME_VERIFIED_LOCAL | Controllers + schemas |
| Preference | CONTRACTED | Cannot auto-mutate Goal |

## Goal Contract (summary)

Immutable versioned object with: objective, success_criteria, invariants, non_goals, forbidden_outcomes, risk, authority bounds, evidence_requirements, validity, termination.

Child goals cannot weaken parent constraints.

## Authority path

```text
Cognition → typed ActionProposal → Authority Kernel → execution token → Tool Gateway
```

Tool Gateway physically rejects actions without valid execution token.

## Epistemic separation

Observation ≠ Belief ≠ Hypothesis ≠ Plan ≠ Commitment ≠ Unknown.  
Reasoning trace ≠ evidence (GOS-I21).

Evidence status is a state machine (not `verified=true`).  
See `docs/EPISTEMIC_INVALIDATION.md`.

## Durable runtime

Temporal (or successor) is an implementation of durable workflows — domain model must not depend on Temporal types.  
`DurableRunner` is a **local harness** (ADR-0002), not Temporal fulfillment.  
Workflow state ≠ epistemic state.

## Definition of Done v0.1

Still the gate for calling the milestone complete — **not** currently claimed:

1. Accept versioned Goal Contract  
2. Build task DAG  
3. Create org: parent + workers  
4. Execute tasks via **Temporal** (CONTRACTED; DurableRunner ≠ Temporal)  
5. Die mid-task  
6. Resume after restart  
7. Store observations separately from beliefs (**RUNTIME_VERIFIED_LOCAL**; Model/Forecast/Decision local-runtime too)  
8. Create claim + evidence  
9. Invalidation marks claim stale  
10. Worker cannot exceed parent authority  
11. Forbidden action never reaches Tool Gateway  
12. External canary action yields Effect Receipt  
13. Event history allows replay (status projection **RUNTIME_VERIFIED_LOCAL**; full body restore limited)  
14. All model calls via provider abstraction  
15. All tool calls via Tool abstraction  
16. Basic OTel traces (**RUNTIME_VERIFIED_LOCAL** in-memory; Temporal-distributed CONTRACTED)  
17. Budget limits operation  
18. Null result persisted  
19. Test: single-agent vs organization  
20. Survival Test with process kill passes (RUNTIME_VERIFIED_HARNESS; other injections STUBBED)

## Milestones

### M0 — Trustworthy Skeleton (current target)

CI green; versioned contracts; immutable goals; default-deny authority; forbidden tools unreachable; process-kill recovery harness; claim invalidation; event persistence; Survival real vs stub split; EnvironmentCompiler + ChangeGate; epistemic graph local; OTel local in-memory.

### M1 — Durable Cognitive Runtime

Temporal + durable shared state (e.g. Postgres) + OTel + Epistemic Graph runtime.

### M2 — Cognitive Organization

Real workers + EnvironmentCompiler runtime + deep repo audit.

## Hypotheses (preregistered)

- H-DUR-001 Durable execution ↑ long-horizon completion  
- H-AUTH-001 External Authority Kernel ↓ unauthorized actions  
- H-EPI-001 Typed epistemic state ↓ contamination / stale decisions  
- H-VER-001 Verification routing > generic LLM critic  
- H-ORG-001 Dynamic organization > fixed topology (heterogeneous long tasks)  
- H-MEM-001 Negative memory ↓ repeated dead ends  
- H-CF-001 Counterfactual memory ↑ decision calibration  
- H-VOI-001 VOI-aware planning ↓ cost per successful decision  
- H-ADAPT-001 Governed self-improvement without regression explosion  
- H-ENV-001 Environment configuration > prompt elongation (after min instruction quality)  
- H-RSN-001 Adaptive reasoning budgets > fixed-high on quality/cost (≠ lower verification)  
- H-EVAL-001 Calibrated evaluator stack > raw LLM judge  
- H-CTX-001 Structured context retrieval > repeated compaction for state integrity  

## Reference tech (2026, replaceable)

Python 3.13+ runtime · Rust Authority · Temporal · PostgreSQL · S3/MinIO · Cedar · SPIFFE-ready · JSON Schema · OpenAPI · OTel · React console (later)
