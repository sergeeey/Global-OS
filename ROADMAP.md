# ROADMAP.md

## Honesty

$$
\text{implemented approximation} \neq \text{fulfilled contract}
$$

Track states in `docs/capability_matrix.json`.  
Architecture V2: `SPEC-ADDENDUM-V2.md`.  
**DCO contracts = P0; recursive hierarchy superiority = P1 experiment (GOS-I30).**

## M0 — Trustworthy Skeleton

- [x] Contracts, CI pins, Goal/Event/Authority/Gateway, Survival process-kill
- [x] EnvironmentCompiler + ChangeGate + MissionAssigner
- [x] Epistemic graph (Observation→…→Commitment) + EvidenceCandidate (GOS-I22)
- [x] Synthetic H-ENV/H-RSN/H-EVAL/H-CTX harnesses (`INCONCLUSIVE_NEEDS_REAL_MODEL`)

## M1 — Reality Contact (active)

Harness-verified durable path exists; **production reality contact still open**:

- [x] TemporalBridge / Postgres / OTel spans / Rust Authority (RUNTIME_VERIFIED_*)
- [x] Production profile → Rust Authority fail-closed (ADR-0007)
- [x] Strong sandbox fail-closed port (ADR-0006; live Docker CI optional)
- [x] Survival suite expanded (13 RUNTIME_INJECTED)
- [x] Docker Reality Contact path + CI (`run_sandboxed_task`, GOS_REQUIRE_DOCKER)
- [x] OTLP Reality Contact path + CI collector compose (GOS_REQUIRE_OTLP)
- [x] Real model provider adapters ×2 + event trail (wire; live keys optional)
- [x] Remaining survival: malicious_document / human_rejection / contradictory_evidence / corrupted_state
- [x] 48h durable soak harness (accelerated; wall via GOS_REQUIRE_48H)
- [ ] Live remote model evals replacing synthetic H-* when keys available
- [ ] Wall-clock 48h production evidence

## M2 — Cognitive Organization (contracts P0; proof P1)

- [x] OrganizationalUnit + MissionContract + manager_workers compiler
- [x] Org topology suite + H-ORG kill criteria (`INCONCLUSIVE_NEEDS_REAL_MODEL`)
- [x] GoalDriftDetector (GOS-I27)
- [x] OrgCompiler ≥3 topologies without declaring a winner (GOS-I30)
- [x] H-ORG measured pipeline (wire/live providers; scientific claim not accepted)
- [ ] H-ORG-001 scientific acceptance vs strong baselines (long-horizon real tasks)
- [ ] InformationLoss_hierarchy metric on real artifacts
- [ ] Adaptive compiler experiments (single → manager → 2-level → 3-level)

## M3 — Recursive Adaptation

- Preference Ledger / Counterfactual / VOI
- Regime detection + gated self-improvement (no T0 self-promote)
- v1.0: 48h+ task with injected failures → LONG_HORIZON / PRODUCTION_PROVEN claims only with evidence

## Definition of Done

См. `SPEC.md` + `SPEC-ADDENDUM-V2.md` §92–93.  
DoD Architecture V2 / PRODUCTION_PROVEN **not claimed**.
