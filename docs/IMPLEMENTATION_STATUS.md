# IMPLEMENTATION_STATUS.md

Generated evidence snapshot. Do not hand-edit claims that contradict tests.

- pytest collected: **143**
- capabilities tracked: **58**

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
| otel_otlp_live_export | RUNTIME_VERIFIED_HARNESS | OTLP HTTP export to external receiver (in-process sink + deploy compose collector); tests/test_otlp_collector_live.py; CI starts otel-collector |
| survival_process_kill | RUNTIME_VERIFIED_HARNESS | Injection.PROCESS_KILL real abort/resume |
| survival_other_injections | RUNTIME_VERIFIED_HARNESS | run_survival_suite 13 RUNTIME_INJECTED incl. MALICIOUS_DOCUMENT/HUMAN_REJECTION/CONTRADICTORY_EVIDENCE/CORRUPTED_STATE; tests/test_survival_multi.py |
| real_model_providers | RUNTIME_VERIFIED_HARNESS | OpenAICompat+Anthropic HTTP adapters (no vendor SDK); RecordingModelProvider model.invoked trail (model/version/cost/latency/output); fail-closed without keys; wire mock + optional live keys; tests/test_model_providers_live.py |
| multi_provider_verification | RUNTIME_VERIFIED_HARNESS | multi_provider_verification_stack openai×anthropic distinct families (GOS-I10); wire HTTP judges + conflicted consensus; tests/test_multi_provider_verification.py |
| goal_integrity_soak_48h | RUNTIME_VERIFIED_HARNESS | run_goal_integrity_soak simulated 48h ACCELERATED_SIMULATED; wall-clock via GOS_REQUIRE_48H; tests/test_survival_soak.py — not PRODUCTION_PROVEN wall 48h |
| full_epistemic_graph | RUNTIME_VERIFIED_LOCAL | tests/test_epistemic.py; Observation→Belief→Claim→Model→Forecast→Decision→Commitment invalidation (GOS-I12) |
| observation_belief_runtime | RUNTIME_VERIFIED_LOCAL | tests/test_observation_belief.py; GOS-I21 guard |
| environment_compiler | RUNTIME_VERIFIED_LOCAL | tests/test_environment_compiler.py (deterministic compile; no model calls) |
| environment_compiler_dynamic | RUNTIME_VERIFIED_LOCAL | EnvironmentChangeGate PROPOSED→…→ACTIVE with authority gate; no silent rewrite (GOS-I20); tests/test_epistemic_graph_env_replay.py |
| sandbox_mvp | RUNTIME_VERIFIED_LOCAL | tests/test_sandbox.py (local process, not container) |
| sandbox_strong | RUNTIME_VERIFIED_HARNESS | run_sandboxed_task network=none + memory limits + destroy; tests/test_sandbox_docker_live.py; CI GOS_REQUIRE_DOCKER=1; nested-overlay hosts may skip |
| source_verification | RUNTIME_VERIFIED_LOCAL | tests/test_source_verification.py (local file resolve) |
| independent_verification_diversity | RUNTIME_VERIFIED_HARNESS | IndependentVerificationStack multi-method consensus; rejects same-model-family LLM judges (GOS-I10); numeric dual stack + remote openai/anthropic judge adapters; tests/test_independent_verification_stack.py; tests/test_multi_provider_verification.py |
| rust_authority_boundary | RUNTIME_VERIFIED_HARNESS | crates/authority_kernel + gos-authority CLI process boundary; GOS-I01/I04/I05; tests/test_rust_authority.py; cargo test |
| repo_audit_structure | RUNTIME_VERIFIED_LOCAL | tests/test_repo_audit.py; gos audit |
| repo_audit_deep | RUNTIME_VERIFIED_LOCAL | deterministic deep static: invariant coverage GOS-I01..I25, forbidden patterns, schema inventory, provider boundary; tests/test_repo_audit.py; not LLM/security pentest |
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
| h_org_001_benchmark | RUNTIME_VERIFIED_HARNESS | summarize_h_org_001 synthetic INCONCLUSIVE; measure_h_org_001 provider-backed wire pipeline (scientific_claim_accepted=false); live keys optional; tests/test_baseline_and_survival.py; tests/test_h_org_measured.py |
| production_profile_rust_authority | RUNTIME_VERIFIED_LOCAL | GOS_PROFILE=production defaults rust + probes gos-authority; forbids python backend; ADR-0007; tests/test_runtime_profile.py |
| spec_addendum_v2 | RUNTIME_VERIFIED_LOCAL | SPEC-ADDENDUM-V2.md normative; CONSTITUTION GOS-I26..I30; DCO P0 vs H-ORG P1 (GOS-I30) |
| goal_drift_detector | RUNTIME_VERIFIED_LOCAL | GoalDriftDetector explore→execute + forbidden_outcome; tests/test_organization.py; GOS-I27 |
| empirical_science_freeze | RUNTIME_VERIFIED_LOCAL | ADR-0009; Goal Integrity Score; H-ENV ladder; H-RSN VUW/Cost; H-ORG-1..4; wall_clock schedule; self-audit; tests/test_empirical_science.py; M1.5/PRODUCTION_PROVEN not claimed |
| incident_system | RUNTIME_VERIFIED_LOCAL | IncidentStore postmortem fields + ledger events; tests/test_path_lock_m15.py |
| dod_v2_gate | RUNTIME_VERIFIED_LOCAL | summarize_dod_v2 closed=false while PARTIALs remain; tests/test_path_lock_m15.py |
| dogfood_mission | RUNTIME_VERIFIED_LOCAL | DogfoodMission ordered stages; autonomous merge forbidden; tests/test_path_lock_m15.py |
| free_model_providers | RUNTIME_VERIFIED_HARNESS | OpenRouter/Groq/Gemini adapters; GOS_ZERO_COST_MODE; scientific pin; free catalog+privacy; tests/test_free_providers.py — live keys user-supplied |
| org_compiler_multi_topology | RUNTIME_VERIFIED_LOCAL | single_solver + manager_workers + parallel_workers; recursive_hierarchy fail-closed; hypothesis_status=UNPROVEN; tests/test_organization.py; GOS-I30 |

