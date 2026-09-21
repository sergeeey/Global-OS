# IMPLEMENTATION_STATUS.md

Generated evidence snapshot. Do not hand-edit claims that contradict tests.

- pytest collected: **54**
- capabilities tracked: **37**

| Capability | State | Evidence |
| ---------- | ----- | -------- |
| goal_contract_immutable | RUNTIME_VERIFIED_LOCAL | tests/test_goal_and_events.py |
| event_ledger_append_only | RUNTIME_VERIFIED_LOCAL | tests/test_goal_and_events.py; tests/test_sql_store.py |
| authority_default_deny | RUNTIME_VERIFIED_LOCAL | tests/test_authority.py; tests/test_policy.py |
| tool_gateway_token_gate | RUNTIME_VERIFIED_LOCAL | tests/test_authority.py |
| effect_receipt | RUNTIME_VERIFIED_LOCAL | tests/test_authority.py |
| claim_invalidation | RUNTIME_VERIFIED_LOCAL | tests/test_epistemic.py |
| durable_runner_process_kill | RUNTIME_VERIFIED_HARNESS | tests/test_durable_recovery.py; tests/test_survival_multi.py |
| temporal_durability | CONTRACTED | SPEC.md DoD #4; ADR-0002 |
| postgres_durable_state | CONTRACTED | migrations/001_init.sql (dialect); SQLite adapter only |
| sql_sqlite_adapter | RUNTIME_VERIFIED_LOCAL | tests/test_sql_store.py |
| otel_traces | RUNTIME_VERIFIED_LOCAL | tests/test_otel.py (in-memory exporter; not Temporal-distributed) |
| otel_distributed_temporal | CONTRACTED | full Goal→Workflow→Activity OTel with Temporal deferred to M1 |
| survival_process_kill | RUNTIME_VERIFIED_HARNESS | Injection.PROCESS_KILL real abort/resume |
| survival_other_injections | STUBBED | scenarios marked fidelity=stub; excluded from GoalIntegritySurvival |
| full_epistemic_graph | RUNTIME_VERIFIED_LOCAL | tests/test_epistemic.py; Observation→Belief→Claim→Model→Forecast→Decision→Commitment invalidation (GOS-I12) |
| observation_belief_runtime | RUNTIME_VERIFIED_LOCAL | tests/test_observation_belief.py; GOS-I21 guard |
| environment_compiler | RUNTIME_VERIFIED_LOCAL | tests/test_environment_compiler.py (deterministic compile; no model calls) |
| environment_compiler_dynamic | RUNTIME_VERIFIED_LOCAL | EnvironmentChangeGate PROPOSED→…→ACTIVE with authority gate; no silent rewrite (GOS-I20); tests/test_epistemic_graph_env_replay.py |
| sandbox_mvp | RUNTIME_VERIFIED_LOCAL | tests/test_sandbox.py (local process, not container) |
| sandbox_strong | CONTRACTED | container/gVisor deferred |
| source_verification | RUNTIME_VERIFIED_LOCAL | tests/test_source_verification.py (local file resolve) |
| independent_verification_diversity | STUBBED | diversity factors recorded; multi-provider path absent |
| rust_authority_boundary | CONTRACTED | semantic contract in Python first |
| repo_audit_structure | RUNTIME_VERIFIED_LOCAL | tests/test_repo_audit.py; gos audit |
| repo_audit_deep | STUBBED | structure scan only |
| hypothesis_lifecycle | RUNTIME_VERIFIED_LOCAL | tests/test_hypotheses.py |
| event_replay_engine | RUNTIME_VERIFIED_LOCAL | EventReplayEngine status projection rebuild from ledger; not full entity-body snapshot restore |
| mission_outcome_contract | RUNTIME_VERIFIED_LOCAL | MissionAssigner outcome-level MissionContract; rejects microstep objectives; tests/test_epistemic_graph_env_replay.py |
| materiality_engine | RUNTIME_VERIFIED_LOCAL | tests/test_materiality_clarification_budget.py |
| clarification_assumption_recording | RUNTIME_VERIFIED_LOCAL | ClarificationEngine → assumption schema + ledger |
| reasoning_budget_controller | RUNTIME_VERIFIED_LOCAL | GOS-I23: effort changes; verification_tier unchanged |
| capability_registry | RUNTIME_VERIFIED_LOCAL | tests/test_env_extensions.py; GOS-I25 |
| context_assembler | RUNTIME_VERIFIED_LOCAL | ContextItem provenance + token budget |
| retrieval_router | RUNTIME_VERIFIED_LOCAL | intent→strategy; GraphRAG not default |
| evaluator_registry | RUNTIME_VERIFIED_LOCAL | GOS-I24 self-judge rejected; calibration fields contracted for production use |
| environment_lifecycle | RUNTIME_VERIFIED_LOCAL | PROPOSED→…→REVOKED transitions |
| h_env_001_benchmark | CONTRACTED | EVALS.md H-ENV-001 preregistered; not yet run |

