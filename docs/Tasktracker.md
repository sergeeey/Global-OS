# Tasktracker

## Done (M0 consolidation)

- [x] Fix invalid `actions/setup-python` immutable SHA (CI unblock)
- [x] Action pin resolve validator (`tools/validate_action_pins.py`)
- [x] Capability matrix CONTRACTED/STUBBED/RUNTIME_VERIFIED*
- [x] Generated `docs/IMPLEMENTATION_STATUS.md` via `tools/project_status.py`
- [x] EnvironmentCompiler contracts + ADR-0003
- [x] ReasoningBudget / ContextManifest / ClarificationPolicy / EnvironmentPolicy / EnvironmentChangeProposal schemas
- [x] Observation / Belief / Commitment schemas + EPISTEMIC_INVALIDATION.md
- [x] GOS-I21 reasoning trace ≠ evidence
- [x] Survival fidelity split; GoalIntegritySurvival excludes stubs
- [x] SPEC/ROADMAP/README formula includes EnvironmentCompiler
- [x] Prior baseline: goal/event/authority/gateway/budget/workers/repo-audit/hypothesis/sandbox/source-verify

## Next (only after M0 green)

- [ ] Minimal OTel (with Temporal, not after)
- [ ] Temporal acceptance: physical kill, no duplicate effects, server/worker unavailable cases
- [ ] Durable shared-state acceptance (concurrent writers, projection rebuild) — Postgres as implementation
- [ ] Epistemic Graph runtime beyond claim←evidence seed
- [ ] Rust Authority boundary after semantic contract freeze
- [ ] Strong sandbox + deep repo-audit
