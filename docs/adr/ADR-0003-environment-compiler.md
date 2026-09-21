# ADR-0003: EnvironmentCompiler as first-class domain

## Context

Model/tool/budget/sandbox/retrieval/context parameters were about to leak into Temporal activities, adapter signatures, events, and OrgUnit contracts without a typed home.

## Problem

Connect Temporal/Postgres/Rust around an incomplete domain model, or freeze environment semantics first?

## Alternatives

1. Keep ad-hoc kwargs on workers/activities  
2. First-class `ExecutionEnvironment` + EnvironmentCompiler contracts before heavy infra (chosen)  
3. Defer until v0.3 organizational compiler

## Decision

Extend the architectural formula:

```text
GlobalOS =
  GoalContract
  + EpistemicKernel
  + DurableRuntime
  + AuthorityKernel
  + DynamicCognitiveOrganization
  + EnvironmentCompiler
  + WorldInteraction
  + VerificationFabric
  + AdaptiveLearning
```

Add schemas (contracts-first, minimal runtime):

- ExecutionEnvironment
- EnvironmentPolicy
- ReasoningBudget
- ContextManifest
- ClarificationPolicy
- EnvironmentChangeProposal

Environment changes are versioned proposals — never silent mutation of an active environment identity.

## Evidence

Leakage risk into Temporal/model adapters/events/telemetry/budget/OrgUnit is immediate once durable workflows land.

## Trade-offs

+ Stable API before infra  
− Slight delay before Temporal wiring

## Reversal trigger

Reconsider only if a single open standard encodes these fields without domain leakage — none exists today.
