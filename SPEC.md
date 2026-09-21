# SPEC.md — Technical Specification v0.1

**Project:** Global OS (ex Goal OS)  
**Date:** 2026-09-21  
**Status:** Initial Architecture Baseline  

## Mission

Maximize useful autonomous work per unit of unverified human trust — not tool-call count, not agent count, not zero human involvement at any cost.

## Formula

$$
\text{GlobalOS} = \text{GoalContract} + \text{EpistemicKernel} + \text{DurableRuntime} + \text{AuthorityKernel} + \text{DynamicCognitiveOrganization} + \text{WorldInteraction} + \text{Verification} + \text{Adaptation}
$$

LLM is interchangeable compute behind adapters.

## Contracts-first rule

Every core entity has: schema, version, ID semantics, state transitions, validation, events, ownership, tests, migration policy.

Sequence: Problem → Contract → Invariant → Tests → Implementation → Runtime evidence.

## Core entities (v0.1)

| Entity | Immature? | Notes |
|--------|-----------|-------|
| GoalContract | no | Immutable versioned; amendments only |
| Event | no | Append-only ledger |
| ActionProposal | no | Normalized typed input to Authority |
| EffectReceipt | no | Required for material actions |
| Evidence / Claim | partial Sprint 3 | Separate from Observation/Belief |
| OrgUnit | partial Sprint 4 | Runtime organization, not personas |
| Preference | schema only | Cannot auto-mutate Goal |

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

Evidence status is a state machine (not `verified=true`).

## Durable runtime

Temporal (or successor) is an implementation of durable workflows — domain model must not depend on Temporal types.  
Workflow state ≠ epistemic state.

## Definition of Done v0.1

1. Accept versioned Goal Contract  
2. Build task DAG  
3. Create org: parent + workers  
4. Execute tasks via Temporal  
5. Die mid-task  
6. Resume after restart  
7. Store observations separately from beliefs  
8. Create claim + evidence  
9. Invalidation marks claim stale  
10. Worker cannot exceed parent authority  
11. Forbidden action never reaches Tool Gateway  
12. External canary action yields Effect Receipt  
13. Event history allows replay  
14. All model calls via provider abstraction  
15. All tool calls via Tool abstraction  
16. Basic OTel traces  
17. Budget limits operation  
18. Null result persisted  
19. Test: single-agent vs organization  
20. Survival Test with process kill passes  

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

## Reference tech (2026, replaceable)

Python 3.13+ runtime · Rust Authority · Temporal · PostgreSQL · S3/MinIO · Cedar · SPIFFE-ready · JSON Schema · OpenAPI · OTel · React console (later)
