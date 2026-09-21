# Changelog

## 0.1.8 — 2026-09-21

### Added

- EvidenceCandidate schema + pipeline (Execution Trace → Candidate → Verification → Evidence)
- GOS-I22 enforcement: tool_result cannot promote to SYSTEM_TRUSTED; CoT rejected

## 0.1.6 — 2026-09-21

### Added

- H-ENV-001 / H-RSN-001 synthetic harnesses (`verdict=INCONCLUSIVE_NEEDS_REAL_MODEL`)
- `connect_durable_store` Postgres URL fail-closed (no silent SQLite fallback)

### Honesty

- Synthetic hint ≠ scientific confirmation of H-ENV-001 / H-RSN-001
- `postgres_durable_state` remains CONTRACTED until real Postgres runtime proof

## 0.1.5 — 2026-09-21

### Added

- ClarificationEngine writes Assumptions into EpistemicStore; STALE on claim/evidence invalidation
- WorkflowRunnerPort + LocalDurableAdapter; TemporalWorkflowAdapter fails closed (ADR-0002 honesty)

### Honesty

- LocalDurableAdapter ≠ Temporal DoD (`temporal_durability` remains CONTRACTED)

## 0.1.4 — 2026-09-21

### Added

- Epistemic Model / Forecast / Decision schemas + store APIs
- Full GOS-I12 invalidation: evidence→claim→model→forecast→decision→commitment
- EnvironmentChangeGate: propose→sandbox→eval→approve→active (authority-gated; no identity rewrite)
- EventReplayEngine: rebuild status projections from append-only ledger
- MissionAssigner: outcome MissionContract for OrgUnit; rejects microstep objectives
- Event types: model.staled, forecast.staled, decision.needs_review, commitment.needs_review,
  environment.change_proposed, environment.lifecycle_transitioned, mission.assigned, projection.rebuilt

### Honesty

- Event replay = status projection rebuild, not full entity-body snapshot restore
- EnvironmentChangeGate ≠ unsupervised adaptive self-rewrite of T0
- Temporal / Postgres / distributed OTel remain CONTRACTED (M1)

## 0.1.3 — 2026-09-21

### Added

- GOS-I22..I25; ADR-0004 (Stable Core / Capability Registry / World Facts)
- Schemas: assumption, capability_descriptor, context_item, mission_contract, evaluator_descriptor
- ClarificationEngine (assumptions recorded), MaterialityEngine, ReasoningBudgetController (GOS-I23)
- CapabilityRegistry, ContextAssembler, RetrievalRouter, EvaluatorRegistry, EnvironmentLifecycle
- Preregistered H-ENV-001, H-RSN-001, H-EVAL-001, H-CTX-001 (EVALS.md)

### Explicitly NOT claimed

- κ≥0.75 constitutional rule
- “80% environment / 20% prompt” as fact
- GraphRAG default / unverified GraphRAG percentages
- Model confidence as truth or verification skip

### Added

- Minimal OTel Goal→Task→Action spans (`global_os.observability`) with in-memory exporter
- Observation/Belief store APIs + obs→belief→claim invalidation; GOS-I21 rejection of reasoning-as-SYSTEM_TRUSTED
- EnvironmentCompiler.compile() from Goal+OrgUnit+Task (schema-validated)

### Honesty

- `otel_traces` = RUNTIME_VERIFIED_LOCAL; `otel_distributed_temporal` remains CONTRACTED
- `environment_compiler` = RUNTIME_VERIFIED_LOCAL compile; dynamic ChangeGate RUNTIME (0.1.4)
- Full Epistemic Graph Model/Forecast/Decision — see 0.1.4

### Fixed

- Invalid immutable pin for `actions/setup-python` (truncated SHA broke CI run #7)
- Survival `GoalIntegritySurvival` no longer counts stub injections as runtime proof

### Added

- `tools/validate_action_pins.py` — full SHA + remote resolve
- `docs/capability_matrix.json` + `tools/project_status.py` → `IMPLEMENTATION_STATUS.md`
- EnvironmentCompiler contracts (ADR-0003): ExecutionEnvironment, EnvironmentPolicy, ReasoningBudget, ContextManifest, ClarificationPolicy, EnvironmentChangeProposal
- Observation / Belief / Commitment schemas + `EPISTEMIC_INVALIDATION.md`
- GOS-I21 — Reasoning trace ≠ evidence
- ScenarioFidelity (`runtime_injected` vs `stub`) for Survival harness

### Changed

- Architectural formula includes EnvironmentCompiler + VerificationFabric + AdaptiveLearning
- SPEC/ROADMAP/Tasktracker realigned to M0/M1/M2; DoD v0.1 not falsely claimed

### Added

- Architecture baseline: CONSTITUTION, SPEC, ARCHITECTURE, models, NON_GOALS, AGENTS, EVALS, ROADMAP, ADR-0001
- JSON Schemas: goal_contract, event, action_proposal, effect_receipt, evidence, claim, org_unit, task
- Python core: GoalStore (immutable versions), EventLedger (append-only), AuthorityKernel (default-deny, GOS-I04), ToolGateway (token-gated + effect receipts), EpistemicStore (invalidation → claim STALE)
- NullResultStore (GOS-I11), ModelProvider/ToolAdapter stubs (no vendor SDK in core)
- CLI `gos goal create|show` / `gos events tail` with local `.gos/` file store
- Example killer use-case goal: `examples/goal_repo_audit.json`
- CI workflow (pinned Actions SHAs), Makefile, schema validator
- Acceptance tests: goal immutability, authority inheritance, gateway denial, idempotency, invalidation, adapters, null results

### Also in 0.1.x follow-up

- BudgetKernel (reserve/commit, cannot go negative/overspend)
- OrganizationCompiler manager_workers + repo-audit task DAG
- Survival Benchmark scaffold (GoalIntegritySurvival metric)
- SQL EventLedger/GoalStore + migrations/001_init.sql
- DurableRunner with process-kill resume (ADR-0002)
- ApprovalService (HMAC, one-time, action_hash bound)
- Cedar base.cedar + PolicyEngine wired into AuthorityKernel
- H-ORG-001 synthetic baseline: single_solver vs manager_workers
- Ephemeral workers + SHA-256 artifact store
- VerificationRouter (tiering + deterministic numeric)
- Repo-audit read-only toolset, E2E smoke, `gos audit`
- Hypothesis lifecycle (Y-17) with null_result on kill
- Sandbox MVP + source verification protocol
- Multi-injection Survival suite (GoalIntegritySurvival=1.0 in harness)

