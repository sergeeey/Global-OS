# docs/adr/ADR-0005-fail-closed-durable-adapters.md

## Context

M1 needs Temporal and Postgres, but CI/dev often lack live servers. Risk: silent fallback to SQLite/LocalDurable that falsely greenlights DoD.

## Problem

How to ship adapter ports without claiming Temporal/Postgres fulfillment?

## Alternatives

1. Require Temporal+Postgres in every CI job from day one  
2. Silent fallback LocalDurable/SQLite when remote unavailable  
3. Optional deps + fail-closed probes; CONTRACTED until runtime evidence (chosen)

## Decision

- `connect_durable_store(postgres://…)` never falls back to SQLite  
- `TemporalWorkflowAdapter` never falls back to `LocalDurableAdapter`  
- Optional extra: `pip install global-os[durable]` (`psycopg`, `temporalio`)  
- Capability matrix keeps `temporal_durability` / `postgres_durable_state` CONTRACTED until kill/shared-state acceptance passes against real services

## Evidence

Tests: unreachable Postgres/Temporal raise `PostgresUnavailable` / `TemporalAdapterUnavailable`.

## Trade-offs

+ Honest capability states  
− Full M1 DoD blocked on infra

## Reversal trigger

Flip states to RUNTIME_VERIFIED_* only after harnesses with real Temporal worker-kill and Postgres concurrent writers pass.
