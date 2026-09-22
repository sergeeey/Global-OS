# Changelog

## 0.1.37 — 2026-09-22

### Mode

- Switch primary cycle to dogfood: Y-17 one-hypothesis mission → failure → fix → replay
- M1.5 remains IN PROGRESS; wall-clock 48h explicitly paused (not blocking real work)

## 0.1.36 — 2026-09-22

### Progress

- Operator live smoke: OpenRouter + Groq + Gemini PASS at cost=0 (local Windows; not claimed as M1.5)
- Operator live H-ENV + measured H-RSN JSON for all three free providers (`scientific_claim_accepted=false`)

## 0.1.35 — 2026-09-22

### Fixed

- Model HTTP client: preserve Authorization on redirects; set User-Agent (Groq CF 1010)
- Sanitize env API keys (BOM/ZWSP/quotes); Gemini errors include finishReason / max_tokens hint

## 0.1.34 — 2026-09-22

### Added

- ENV-REAL-001: observed Cloud Agent vs local-secret locality failure (H-ENV datapoint; claim false)

## 0.1.33 — 2026-09-21

### Added

- `.env.example` — safe free-tier key template (Git Bash / PowerShell load notes)

## 0.1.32 — 2026-09-21

### Changed

- Free model pins: OpenRouter `nvidia/nemotron-3-ultra-550b-a55b:free`, Groq `openai/gpt-oss-120b`,
  Gemini `gemini-3.6-flash` (deprecated qwen3-32b / gemini-2.0-flash removed)

### Added

- `run_hrsn_measured` — real provider calls for fixed L/M/H vs adaptive (claim still false)
- Schedule-driven 48h soak (`run_scheduled_48h_soak` / `WALL_CLOCK_48H_SCHEDULE`)

## 0.1.31 — 2026-09-21

### Added

- Free providers: OpenRouter / Groq / Gemini adapters (OpenAI-compat + Gemini HTTP)
- `GOS_ZERO_COST_MODE=1` denies paid OpenAI/Anthropic and cost_usd>0
- Scientific pin: `openrouter/free` forbidden; model substitution fail-closed + `model.substituted` event
- Free model Capability Registry catalog + privacy/training_allowed
- ExecutionEnvironment optional `data_policy` (public/confidential)

### Honesty

- Live free-tier evals still need user-supplied `OPENROUTER_API_KEY` / `GROQ_API_KEY` / `GEMINI_API_KEY`
- Do not send confidential data to training-possible free providers

## 0.1.30 — 2026-09-21

### Added

- Path lock: M1.5 → DoD V2 → M2 → M3 → per-capability PRODUCTION_PROVEN
- `IncidentStore` + `incident.schema.json` (postmortem-required fields)
- DoD V2 evidence gate (`summarize_dod_v2`, currently `closed=false`)
- Dogfooding mission stages through `request_merge`; autonomous merge fail-closed

### Honesty

- No new architecture layers; tooling for Measure→Falsify→Learn only

## 0.1.29 — 2026-09-21

### Added

- ADR-0009 Empirical Science freeze + M1.5 Operationally Validated gate
- Goal Integrity Score (8 hard PASS/FAIL gates; soft metrics never rescue)
- H-ENV A–E ladder contract (`run_henv_ladder`; E not required to win)
- H-RSN fixed-low/medium/high vs adaptive (`VerifiedUsefulWork/Cost`, GOS-I23)
- H-ORG-1..4 hypothesis split + conditional synthetic map (claims not accepted)
- Wall-clock 48h injection schedule (release gate, not PR)
- Capability self-audit (`audit_capability_matrix`)

### Honesty

- M1 nearly closed; M1.5 / PRODUCTION_PROVEN not claimed
- Architecture → Empirical Science; no new kernel layers until live evidence

## 0.1.28 — 2026-09-21

### Fixed

- Action pin validator retries on GitHub API 403/429; CI passes `GITHUB_TOKEN` to avoid rate-limit flakes

## 0.1.27 — 2026-09-21

### Added

- H-ORG-001 measured path: `measure_h_org_001` / `summarize_h_org_001_measured`
- Heterogeneous micro-task suite vs single_solver / manager_workers with provider + event trail
- Wire pipeline verdict `WIRE_MEASURED_PIPELINE_OK_NOT_SCIENTIFIC`; live keys → `LIVE_MODEL_*`

### Honesty

- `scientific_claim_accepted` always false until larger long-horizon evidence (GOS-I30)
- Without keys, default remains `INCONCLUSIVE_NEEDS_REAL_MODEL`

## 0.1.26 — 2026-09-21

### Added

- Real model providers: `OpenAICompatProvider` + `AnthropicProvider` (stdlib HTTP, no vendor SDK)
- `RecordingModelProvider` → `model.invoked` event trail (model/version/cost/latency/output digest)
- Fail-closed without API keys; wire-path dual-provider tests; optional live keys (`GOS_REQUIRE_MODELS`)
- Survival RUNTIME_INJECTED: MALICIOUS_DOCUMENT, HUMAN_REJECTION, CONTRADICTORY_EVIDENCE, CORRUPTED_STATE (13 total)
- `EpistemicStore.mark_contradicted` + `CorruptedCheckpointError` (GOS-I16/I26/I29)
- Multi-provider verification adapters (`multi_provider_verification_stack`)
- Accelerated 48h `GoalIntegritySurvival` soak (`run_goal_integrity_soak`; wall via `GOS_REQUIRE_48H`)

### Honesty

- Live remote model calls not claimed without keys; soak fidelity=`ACCELERATED_SIMULATED` unless `GOS_REQUIRE_48H`
- H-ORG-001 measured superiority still `INCONCLUSIVE_NEEDS_REAL_MODEL` / P1

## 0.1.25 — 2026-09-21

### Added

- Reality Contact infra: `deploy/docker-compose.reality.yml` + OTLP collector config
- `run_sandboxed_task` — Goal/Task → container → network/limits check → destroy
- Live tests: `test_sandbox_docker_live.py`, `test_otlp_collector_live.py` (OTLP HTTP sink + optional compose)
- CI requires Docker containers + OTLP collector (`GOS_REQUIRE_DOCKER` / `GOS_REQUIRE_OTLP`)

## 0.1.24 — 2026-09-21

### Added

- `SPEC-ADDENDUM-V2.md` — normative Architecture V2 extension
- GOS-I26…I30 (external instruction taint, goal drift, maturity evidence, no invented state, topology≠truth)
- `GoalDriftDetector` (GOS-I27)
- OrgCompiler `single_solver` / `parallel_workers` / `manager_workers`; contracted topologies fail-closed (GOS-I30)
- `organization_graph.schema.json`; DCO contracts P0 vs H-ORG proof P1 in ROADMAP/AGENTS

## 0.1.23 — 2026-09-21

### Added

- Survival injections: API_OUTAGE, MODEL_SWAP, SLOW_DEPENDENCY, CONSTRAINT_CHANGE
- `OutageModelProvider` / `SwappableModelProvider` / `SlowModelProvider` fail-closed stubs

## 0.1.22 — 2026-09-21

### Added

- `GOS_PROFILE=dev|production` — production defaults Authority to Rust + startup probe (ADR-0007)
- `ProductionProfileError` fail-closed when binary missing or python backend forced in production

## 0.1.21 — 2026-09-21

### Added

- H-ORG-001 full topology suite (flat swarm → dynamically compiled) + kill-criteria evaluator
- `summarize_h_org_001` → `INCONCLUSIVE_NEEDS_REAL_MODEL`; `h_org_001_benchmark` tracked

## 0.1.20 — 2026-09-21

### Added

- Strong sandbox port: `open_sandbox` / `ContainerSandbox` / `probe_docker` (ADR-0006)
- Fail-closed for `container` without Docker and for unimplemented `gvisor`/`microvm`
- `sandbox_strong` → RUNTIME_VERIFIED_LOCAL (live Docker isolation not claimed without daemon)

## 0.1.19 — 2026-09-21

### Added

- Survival harness runtime injections: FALSE_TOOL_SUCCESS, SOURCE_INVALIDATION, DUPLICATE_ACTION, BUDGET_REDUCTION
- `run_survival_suite()`; `survival_other_injections` → RUNTIME_VERIFIED_HARNESS

### Honesty

- Injection enum still lists unimplemented kinds (API_OUTAGE, MODEL_SWAP, …) outside DEFAULT_SCENARIOS

## 0.1.18 — 2026-09-21

### Added

- Deep repo audit (`depth=deep`): invariant coverage, forbidden-pattern scan, schema inventory, provider-boundary heuristic
- `repo_audit_deep` → RUNTIME_VERIFIED_LOCAL (deterministic static; not LLM pentest)

## 0.1.17 — 2026-09-21

### Added

- `IndependentVerificationStack` — multi-method consensus with distinct diversity axes (GOS-I10)
- Rejects same-model-family LLM-only stacks; conflicted outcomes are first-class (GOS-I16)
- Numeric dual deterministic stack wired into `VerificationRouter` for tier ≥ INDEPENDENT
- `independent_verification_diversity` → RUNTIME_VERIFIED_LOCAL

### Honesty

- Local multi-method diversity verified; remote multi-provider adapters still optional

## 0.1.16 — 2026-09-21

### Added

- OTLP HTTP exporter config (`configure_otlp_exporter`) — fail-closed when endpoint unset or exporter package missing (`OtlpExportError`)
- Optional dependency `global-os[otel]` (`opentelemetry-exporter-otlp-proto-http`)
- `otel_otlp_fail_closed` → RUNTIME_VERIFIED_LOCAL

### Honesty

- Live OTLP collector export still not claimed as PRODUCTION_PROVEN

## 0.1.15 — 2026-09-21

### Added

- `AuthorityKernel(backend="rust"|"python")` / `GOS_AUTHORITY_BACKEND` — prefer Rust process boundary

## 0.1.14 — 2026-09-21

### Added

- Rust `authority_kernel` crate + `gos-authority` CLI (process boundary)
- Python `decide_via_rust` fail-closed client
- CI builds/tests Rust Authority before pytest
- `rust_authority_boundary` → RUNTIME_VERIFIED_HARNESS

## 0.1.12 — 2026-09-21

### Added

- OTel Workflow + Activity spans on TemporalBridge path
- `otel_distributed_temporal` → RUNTIME_VERIFIED_LOCAL (in-process time-skipping; collector export not claimed)

## 0.1.11 — 2026-09-21

### Added

- TemporalBridge (GosGoalExecution workflow + gos_run_step activity)
- Kill/retry harness: no duplicate material effects
- `temporal_durability` → RUNTIME_VERIFIED_HARNESS (time-skipping Temporal env)

### Honesty

- Multi-worker live restart still reserved for TEMPORAL_ADDRESS path
- LocalDurableAdapter ≠ TemporalBridge

## 0.1.10 — 2026-09-21

### Added

- PostgresEventLedger + reconnect/concurrent-writer acceptance harness
- CI `postgres:16` service + `GOS_TEST_DATABASE_URL`
- Sequence-safe concurrent seq allocation (`gos_events_seq`)

### Changed

- `postgres_durable_state` → RUNTIME_VERIFIED_HARNESS
- `temporal_durability` remains CONTRACTED

## 0.1.9 — 2026-09-21

### Added

- ADR-0005 fail-closed durable adapters
- Temporal probe + Postgres connect fail-closed (optional `[durable]` extras)
- `apply_postgres_migrations` helper (requires live Postgres)

### Honesty

- `temporal_durability` / `postgres_durable_state` remain CONTRACTED

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

