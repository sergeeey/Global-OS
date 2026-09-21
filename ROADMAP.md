# ROADMAP.md

## Honesty

$$
\text{implemented approximation} \neq \text{fulfilled contract}
$$

Track states in `docs/capability_matrix.json`.

## M0 — Trustworthy Skeleton (active)

- [x] CONSTITUTION (+ GOS-I21), SPEC, ARCHITECTURE, models, NON_GOALS, AGENTS, EVALS
- [x] Core JSON schemas + EnvironmentCompiler contracts (ADR-0003)
- [x] Observation / Belief / Commitment schemas + invalidation contract doc
- [x] CI with resolvable Action SHA pins + pin validator
- [x] Goal / Event / Authority / Gateway / Budget (local runtime verified)
- [x] DurableRunner process-kill harness (≠ Temporal)
- [x] Survival: runtime_injected vs stub split
- [x] Capability matrix + generated IMPLEMENTATION_STATUS
- [x] Minimal OTel traces (local in-memory; Temporal-distributed still CONTRACTED)
- [x] CI green on `main` (post consolidation)
- [x] Observation/Belief runtime seed + EnvironmentCompiler.compile()

## M1 — Durable Cognitive Runtime

- Temporal adapter with physical worker-kill + no duplicate material effects
- Durable shared state surviving process/container loss + concurrent writers (Postgres is one implementation)
- OTel Goal→…→Action traces
- Full Epistemic Graph runtime (Observation→…→Commitment) with recursive invalidation

## M2 — Cognitive Organization

- EnvironmentCompiler runtime
- Deep repo-audit (beyond structure scan)
- Real multi-injection Survival (not stub catalog)
- H-ORG-001 with measured baselines

## Later

- Rust Authority process boundary (after semantic contract stable)
- Strong sandbox (container/gVisor)
- Preference Ledger / Counterfactual / VOI
- v1.0: 48h+ task with injected failures

## Definition of Done v0.1

См. `SPEC.md` — not claimed complete until Temporal + OTel + observation/belief runtime separation are RUNTIME_VERIFIED.
