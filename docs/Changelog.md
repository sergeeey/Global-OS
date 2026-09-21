# Changelog

## 0.1.0 — 2026-09-21

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

