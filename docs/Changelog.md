# Changelog

## 0.1.2 — 2026-09-21

### Added

- Minimal OTel Goal→Task→Action spans (`global_os.observability`) with in-memory exporter
- Observation/Belief store APIs + obs→belief→claim invalidation; GOS-I21 rejection of reasoning-as-SYSTEM_TRUSTED
- EnvironmentCompiler.compile() from Goal+OrgUnit+Task (schema-validated)

### Honesty

- `otel_traces` = RUNTIME_VERIFIED_LOCAL; `otel_distributed_temporal` remains CONTRACTED
- `environment_compiler` = RUNTIME_VERIFIED_LOCAL compile; dynamic recompilation CONTRACTED
- Full Epistemic Graph still not claimed (Model/Forecast/Decision deferred)

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

