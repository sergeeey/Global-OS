# IMPLEMENTATION_STATUS.md

Generated evidence snapshot. Do not hand-edit claims that contradict tests.

- pytest collected: **40**
- capabilities tracked: **27**

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
| full_epistemic_graph | STUBBED | Observation/Belief runtime + obs→belief→claim invalidation; Model/Forecast/Decision nodes still CONTRACTED |
| observation_belief_runtime | RUNTIME_VERIFIED_LOCAL | tests/test_observation_belief.py; GOS-I21 guard |
| environment_compiler | RUNTIME_VERIFIED_LOCAL | tests/test_environment_compiler.py (deterministic compile; no model calls) |
| environment_compiler_dynamic | CONTRACTED | adaptive recompilation / change proposals runtime deferred |
| sandbox_mvp | RUNTIME_VERIFIED_LOCAL | tests/test_sandbox.py (local process, not container) |
| sandbox_strong | CONTRACTED | container/gVisor deferred |
| source_verification | RUNTIME_VERIFIED_LOCAL | tests/test_source_verification.py (local file resolve) |
| independent_verification_diversity | STUBBED | diversity factors recorded; multi-provider path absent |
| rust_authority_boundary | CONTRACTED | semantic contract in Python first |
| repo_audit_structure | RUNTIME_VERIFIED_LOCAL | tests/test_repo_audit.py; gos audit |
| repo_audit_deep | STUBBED | structure scan only |
| hypothesis_lifecycle | RUNTIME_VERIFIED_LOCAL | tests/test_hypotheses.py |
| event_replay_engine | STUBBED | list_events available; full replay/projection rebuild contracted |

