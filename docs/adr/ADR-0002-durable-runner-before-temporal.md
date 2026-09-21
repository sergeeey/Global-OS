# docs/adr/ADR-0002-durable-runner-before-temporal.md

## Context

Sprint 1 needs crash/recovery proof (DoD #5–6, #20) before Temporal ops cost is justified.

## Problem

Bind domain workflows to Temporal SDK types too early, or invent a throwaway runner?

## Alternatives

1. Require Temporal server in CI from day one  
2. Domain DurableRunner + SQL checkpoints; Temporal as later adapter (chosen)  
3. Only in-memory retry (no persistence)

## Decision

Ship `DurableRunner` with SQL checkpoints and Temporal-shaped step model. Domain workflow state ≠ Temporal types. Temporal becomes an adapter when durable ops are needed at scale.

## Evidence

Recovery test: kill after step → new runner instance resumes → SUCCEEDED.

## Trade-offs

+ Fast CI, no Temporal dependency yet  
− Must keep adapter boundary honest when Temporal lands

## Reversal trigger

Adopt Temporal when Survival Benchmark exceeds single-process SQLite fidelity (multi-worker, timers, signals) or ops requires Temporal Cloud.
