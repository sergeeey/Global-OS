# ADR-0001: System Boundaries

## Context

Global OS must outlive models, tool protocols, and workflow engines. First commit must not be `agent.py`.

## Problem

Where is the stable system boundary vs replaceable implementation?

## Alternatives

1. Agent-framework-first (LangGraph/Crew/etc as core)  
2. Pure Temporal/K8s orchestration as domain model  
3. Contracts + invariants + microkernel domains (chosen)

## Decision

- Domain contracts and constitution are the system.  
- Temporal, MCP, A2A, providers, vector search are adapters.  
- Authority Kernel is a separate trust boundary (no model calls inside).  
- Epistemic state is typed and separate from workflow state.  
- Start modular monolith; split physically later without changing contracts.

## Evidence

Industry durable-agent APIs and Temporal prove long-running execution is needed, but binding the domain to one vendor would violate the architectural horizon (§3 of charter).

## Trade-offs

+ Replaceable compute and tools  
+ Clear security boundary  
− Slower first demo than “spawn agents now”  
− Dual language path (Python + Rust) adds ops cost early

## Reversal trigger

Reconsider if: (a) a single durable runtime becomes a formal open standard that encodes our domain events without leaky abstractions, or (b) Authority Kernel latency/ops cost proven to dominate without security benefit in Survival Benchmark (H-AUTH-001 kill).
