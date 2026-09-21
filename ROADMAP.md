# ROADMAP.md

## Honesty

$$
\text{implemented approximation} \neq \text{fulfilled contract}
$$

Track states in `docs/capability_matrix.json`.

## M0 — Trustworthy Skeleton

- [x] Contracts, CI pins, Goal/Event/Authority/Gateway, Survival process-kill
- [x] EnvironmentCompiler + ChangeGate + MissionAssigner
- [x] Epistemic graph (Observation→…→Commitment) + EvidenceCandidate (GOS-I22)
- [x] Synthetic H-ENV/H-RSN/H-EVAL/H-CTX harnesses (`INCONCLUSIVE_NEEDS_REAL_MODEL`)

## M1 — Durable Cognitive Runtime (largely harness-verified)

- [x] TemporalBridge + kill/retry + live multi-worker restart (RUNTIME_VERIFIED_HARNESS)
- [x] Postgres durable shared-state reconnect + concurrent writers (RUNTIME_VERIFIED_HARNESS)
- [x] OTel Goal/Task/Action + Workflow/Activity spans (RUNTIME_VERIFIED_LOCAL; collector export optional)
- [x] Rust Authority process boundary + `AuthorityKernel(backend=rust)`
- [ ] Real-model H-ENV/H-RSN measured runs (replace synthetic)

## M2 — Cognitive Organization

- [ ] Deep repo-audit (beyond structure scan)
- [ ] Real multi-injection Survival (not stub catalog)
- [ ] H-ORG-001 with measured baselines
- [ ] Strong sandbox (container/gVisor)

## Later

- Preference Ledger / Counterfactual / VOI
- Default production profile `GOS_AUTHORITY_BACKEND=rust`
- v1.0: 48h+ task with injected failures

## Definition of Done v0.1

См. `SPEC.md`. Temporal + Postgres + OTel path now have RUNTIME_VERIFIED_* harness evidence;
DoD v0.1 still not claimed as PRODUCTION_PROVEN.
