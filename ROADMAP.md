# ROADMAP.md

## Sprint 0 — Architecture Baseline ✅ (in progress)

- CONSTITUTION, SPEC, ARCHITECTURE, threat/authority/epistemic/org models
- NON_GOALS, AGENTS, EVALS
- contracts (JSON Schema)
- ADR-0001 system boundaries
- repo skeleton + CI schema validation

## Sprint 1 — Goal + Durable Ledger

- Goal Contract create/amend (immutable versions)
- Event Ledger (append-only)
- Postgres persistence
- Temporal Goal Workflow skeleton
- crash/recovery smoke test

## Sprint 2 — Authority

- Identity principal
- Authority Kernel (Rust service or Python stub → Rust)
- Cedar policies
- Tool Gateway + execution token
- fake tools + approval tokens

## Sprint 3 — Epistemic Kernel

- Observation / Claim / Evidence
- Invalidation engine
- Evidence status machine
- Null results storage

## Sprint 4 — Organization

- Worker abstraction
- OrgUnit
- manager-workers topology
- artifact store (content-addressed)

## Sprint 5 — Verification Plane

- Verification Router
- deterministic verifier
- independent verifier diversity tracking

## Sprint 6 — First real task

- sandbox
- repo-audit toolset
- killer use case: GitHub repository audit (read-only)

## Sprint 7 — Survival Benchmark

- process kill / model swap / false tool success
- single-agent vs manager-workers baseline

## Sprint 8 — Organizational Compiler

- recursive hierarchy
- compiler v0
- H-ORG-001 experiment

## Definition of Done v0.1

См. `SPEC.md` § DoD v0.1 (20 пунктов).

## v1.0 gate

48h+ real task with injected failures; 0 unauthorized material actions; 100% receipts; restart recovery; baseline advantage; independent audit.
