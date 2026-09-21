# IMPLEMENTATION_STATUS.md

Generated evidence snapshot. Do not hand-edit claims that contradict tests.

- pytest collected: **85**
- capabilities tracked: **44**

| Capability | State | Evidence |
| ---------- | ----- | -------- |
| goal_contract_immutable | RUNTIME_VERIFIED_LOCAL | tests/test_goal_and_events.py |
| event_ledger_append_only | RUNTIME_VERIFIED_LOCAL | tests/test_goal_and_events.py; tests/test_sql_store.py |
| authority_default_deny | RUNTIME_VERIFIED_LOCAL | tests/test_authority.py; tests/test_policy.py |
| tool_gateway_token_gate | RUNTIME_VERIFIED_LOCAL | tests/test_authority.py |
| effect_receipt | RUNTIME_VERIFIED_LOCAL | tests/test_authority.py |
| claim_invalidation | RUNTIME_VERIFIED_LOCAL | tests/test_epistemic.py |
| durable_runner_process_kill | RUNTIME_VERIFIED_HARNESS | tests/test_durable_recovery.py; tests/test_survival_multi.py |
| temporal_durability | RUNTIME_VERIFIED_HARNESS | TemporalBridge + time-skipping env; kill/retry without duplicate material effects; tests/test_temporal_bridge.py (≠ LocalDurable) |
| postgres_durable_state | RUNTIME_VERIFIED_HARNESS | PostgresEventLedger reconnect + concurrent writers; tests/test_postgres_acceptance.py; CI postgres:16 service |
| sql_sqlite_adapter | RUNTIME_VERIFIED_LOCAL | tests/test_sql_store.py |
| otel_traces | RUNTIME_VERIFIED_LOCAL | tests/test_otel.py (in-memory exporter + OTLP fail-closed without endpoint/package; live collector export not claimed) |
| otel_distributed_temporal | RUNTIME_VERIFIED_LOCAL | TemporalBridge Workflow+Activity spans (time-skipping env); tests/test_temporal_bridge.py::test_temporal_otel_workflow_activity_spans; cross-process OTel collector export still not claimed |
| otel_otlp_fail_closed | RUNTIME_VERIFIED_LOCAL | configure_otlp_exporter raises OtlpExportError when endpoint unset or exporter package missing; tests/test_otel.py |
| survival_process_kill | RUNTIME_VERIFIED_HARNESS | Injection.PROCESS_KILL real abort/resume |
| survival_other_injections | STUBBED | scenarios marked fidelity=stub; excluded from GoalIntegritySurvival |
| full_epistemic_graph | RUNTIME_VERIFIED_LOCAL | tests/test_epistemic.py; Observation→Belief→Claim→Model→Forecast→Decision→Commitment invalidation (GOS-I12) |
| observation_belief_runtime | RUNTIME_VERIFIED_LOCAL | tests/test_observation_belief.py; GOS-I21 guard |
| environment_compiler | RUNTIME_VERIFIED_LOCAL | tests/test_environment_compiler.py (deterministic compile; no model calls) |
| environment_compiler_dynamic | RUNTIME_VERIFIED_LOCAL | EnvironmentChangeGate PROPOSED→…→ACTIVE with authority gate; no silent rewrite (GOS-I20); tests/test_epistemic_graph_env_replay.py |
| sandbox_mvp | RUNTIME_VERIFIED_LOCAL | tests/test_sandbox.py (local process, not container) |
| sandbox_strong | CONTRACTED | container/gVisor deferred |
| source_verification | RUNTIME_VERIFIED_LOCAL | tests/test_source_verification.py (local file resolve) |
| independent_verification_diversity | RUNTIME_VERIFIED_LOCAL | IndependentVerificationStack multi-method consensus; rejects same-model-family LLM judges (GOS-I10); numeric dual deterministic stack; tests/test_independent_verification_stack.py; remote multi-provider adapters still optional |
| rust_authority_boundary | RUNTIME_VERIFIED_HARNESS | crates/authority_kernel + gos-authority CLI process boundary; GOS-I01/I04/I05; tests/test_rust_authority.py; cargo test |
| repo_audit_structure | RUNTIME_VERIFIED_LOCAL | tests/test_repo_audit.py; gos audit |
| repo_audit_deep | STUBBED | structure scan only |
| hypothesis_lifecycle | RUNTIME_VERIFIED_LOCAL | tests/test_hypotheses.py |
| event_replay_engine | RUNTIME_VERIFIED_LOCAL | EventReplayEngine status projection rebuild from ledger; not full entity-body snapshot restore |
| mission_outcome_contract | RUNTIME_VERIFIED_LOCAL | MissionAssigner outcome-level MissionContract; rejects microstep objectives; tests/test_epistemic_graph_env_replay.py |
| materiality_engine | RUNTIME_VERIFIED_LOCAL | tests/test_materiality_clarification_budget.py |
| clarification_assumption_recording | RUNTIME_VERIFIED_LOCAL | ClarificationEngine → EpistemicStore + assumption STALE on claim/evidence invalidation |
| reasoning_budget_controller | RUNTIME_VERIFIED_LOCAL | GOS-I23: effort changes; verification_tier unchanged |
| capability_registry | RUNTIME_VERIFIED_LOCAL | tests/test_env_extensions.py; GOS-I25 |
| context_assembler | RUNTIME_VERIFIED_LOCAL | ContextItem provenance + token budget |
| retrieval_router | RUNTIME_VERIFIED_LOCAL | intent→strategy; GraphRAG not default |
| evaluator_registry | RUNTIME_VERIFIED_LOCAL | GOS-I24 self-judge rejected; calibration fields contracted for production use |
| environment_lifecycle | RUNTIME_VERIFIED_LOCAL | PROPOSED→…→REVOKED transitions |
| h_env_001_benchmark | RUNTIME_VERIFIED_LOCAL | Synthetic harness summarize_h_env_001; verdict INCONCLUSIVE_NEEDS_REAL_MODEL (not scientific confirmation) |
| workflow_runner_port | RUNTIME_VERIFIED_LOCAL | LocalDurableAdapter wraps DurableRunner; TemporalWorkflowAdapter fails closed (≠ Temporal DoD) |
| h_rsn_001_benchmark | RUNTIME_VERIFIED_LOCAL | Synthetic harness summarize_h_rsn_001 + GOS-I23; INCONCLUSIVE_NEEDS_REAL_MODEL |
| postgres_connection_port | RUNTIME_VERIFIED_LOCAL | connect_durable_store fails closed on postgres URL without psycopg; no silent SQLite fallback |
| evidence_candidate_pipeline | RUNTIME_VERIFIED_LOCAL | GOS-I22 EvidenceCandidatePipeline; tool_result↛SYSTEM_TRUSTED; tests/test_evidence_candidate.py |
| temporal_fail_closed_probe | RUNTIME_VERIFIED_LOCAL | TemporalWorkflowAdapter.probe_server fails closed; ≠ Temporal DoD |
| postgres_fail_closed_connect | RUNTIME_VERIFIED_LOCAL | connect_durable_store unreachable/missing-psycopg → PostgresUnavailable; no SQLite fallback |

