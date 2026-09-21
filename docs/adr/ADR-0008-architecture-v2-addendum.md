# docs/adr/ADR-0008-architecture-v2-addendum.md

## Context

Skeleton implements much of Global OS V1 thinking. A supplemental normative architecture text clarifies EnvironmentCompiler, DCO, epistemic/authority separation, and research hypotheses.

## Problem

Risk of treating recursive hierarchy as architectural truth, or rewriting the repo each cycle with a new architecture story.

## Decision

1. Adopt `SPEC-ADDENDUM-V2.md` as Architecture V2 baseline.  
2. **DCO contracts = P0**; **H-ORG topology superiority = P1 experiment** (GOS-I30).  
3. Extend CONSTITUTION with GOS-I26…I30 (mapping table in addendum §95).  
4. Migrate via adapters; no greenfield rewrite (§97).

## Evidence

`SPEC-ADDENDUM-V2.md`, CONSTITUTION v0.2.0, GoalDriftDetector + multi-topology OrgCompiler tests.

## Trade-offs

+ Stable target architecture for agents  
− Large remaining Reality Contact gap (real model/Docker/collector/48h)
