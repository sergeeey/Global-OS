# Tasktracker

## Done

- [x] M0 consolidation + OTel/Observation/Belief/EnvironmentCompiler
- [x] GOS-I22..I25 (trace≠fact, budget≠verification, judge≠self, three layers)
- [x] Assumption schema + ClarificationEngine (ask/assume → recorded assumption)
- [x] Materiality engine + ReasoningBudgetController
- [x] Capability Registry + ContextAssembler + RetrievalRouter
- [x] EvaluatorRegistry (no self-judge) + Environment lifecycle
- [x] MissionContract schema + H-ENV/RSN/EVAL/CTX in EVALS
- [x] ADR-0004 three-layer separation
- [x] Epistemic Model/Forecast/Decision/Commitment invalidation chain (GOS-I12)
- [x] EnvironmentChangeGate (PROPOSED→…→ACTIVE, authority-gated, GOS-I20)
- [x] EventReplayEngine status projection rebuild
- [x] MissionAssigner outcome-first (rejects microsteps)

## Next (M1)

- [ ] Temporal adapter + physical kill acceptance
- [ ] Durable shared-state acceptance (Postgres as one impl)
- [ ] Distributed OTel with workflows
- [ ] Run H-ENV-001 / H-RSN-001 benchmarks (not claim results early)
- [ ] Assumption invalidation wiring into full graph events
- [ ] Rust Authority boundary after contract freeze
