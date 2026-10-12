# ADR-0013 — Competitor primitives borrow (operational, not LLM-as-OS)

## Status

Accepted — 2026-10-12

## Context

Competitive analysis (AIOS, Letta, OpenHands, Temporal, LangGraph, MetaGPT,
PaperQA2, AI Scientist, …) identified useful **operational primitives** while
forbidding philosophy that breaks Global OS invariants (LLM-as-OS, LLM security
oracle, vector-DB-as-truth, fixed swarm as architecture).

M1.5 is `CLOSED_SCOPE_LIMITED`. Soft architecture freeze (ADR-0009) still bars
unplanned T0/T1 kernels; adapter deepenings and T2 skill packs are the intended
borrow path.

## Decision

### Borrow (allowed)

| Source | Primitive | Trust zone | Notes |
|--------|-----------|------------|-------|
| Temporal | Heartbeats, approval Signals, Continue-As-New | Adapter | Deepen TemporalBridge; no Temporal-clone (NON_GOALS) |
| OpenHands | RiskAssessment ≠ ConfirmationPolicy; sandbox isolation | Adapter / World | Deterministic risk only — **never** LLM security score |
| Letta | Progressive disclosure + commit-boundary memory | T2 Memory | Not archival/vector as truth; epistemic types preserved |
| AIOS | Fair LLM resource scheduler (FIFO/RR) | Adapter (models) | Resource OS only; Authority Kernel unchanged |
| MetaGPT | Artifact-first SOP packs | T2 skills | OrgCompiler chooses topology; GOS-I30 stands |
| PaperQA2 | claim→citation→passage grounding | Verification | Strengthens EvidenceCandidate / source path |
| LangGraph | Time-travel UX over ledger | CLI / ops | Not StateGraph-as-architecture |
| AI Scientist | Mission stage templates | T2 / missions | LLM peer-review = advisory only (GOS-I10/I24) |

### Never borrow

- LLM in center of OS / LLM boolean security / LLM peer-review as VERIFIED
- Vector DB or MemGPT archival as truth store
- Fixed N-agent swarm as architectural default
- Second durable engine replacing Temporal adapter boundary
- “Hierarchy wins” as axiom (GOS-I30)

## Consequences

+ Clear path to close DoD V2 PARTIALs with measured evidence.
+ Preserves Intelligence ≠ Authority and NON_GOALS.
− Feature velocity gated by acceptance tests + honesty matrix updates.
− New T0/T1 kernels still require a dedicated ADR + human merge.

## Tracking

`artifacts/hardening/BORROW_ROADMAP.md`
