# EXECUTIVE_AUDIT — Global OS Pre-Production Readiness

**Audit mode:** Autonomous / Read-Only Engineering Review  
**Repo tip audited:** `5a7870b78cec39648521863ce48338709ad0a643` (`origin/main`)  
**Integration tip claimed:** `1372671` (PREPROD+CTC merge; docs tip includes #45/#46)  
**Date:** 2026-10-14  
**Terminal:** `AUDIT_COMPLETE`  
**Pre-production declaration:** **NOT READY** (`v0.1.0-pre` must not be declared)

## One-line verdict

Global OS on `main` has a **working supervised Operator pilot** for a single deterministic read-only mission (`repo.audit` → Completion Gate → `delivery.json`), with strong false-SUCCESS guards for that pilot — but it is **not** yet a system that takes an arbitrary large human goal, plans with a live LLM, uses general tools, and delivers independently verified products.

## Original goal fit

| Aspiration | Fit on tip |
|------------|------------|
| Human sets a large goal | **PARTIAL** — GoalContract schema + one example Goal |
| System organizes execution | **PARTIAL** — OrgCompiler/MissionAssigner/Achiever present; observe path hardcoded |
| Works with real tools | **PARTIAL** — ToolGateway + one sandboxed tool; no general tool loop |
| Recovers from errors | **VERIFIED** (SQLite DurableRunner + durable gate e2e) within step boundaries |
| Verifies result | **VERIFIED** for repo-audit semantics; **NOT** general semantic verification |
| Delivers checkable product | **VERIFIED** for this pilot (`delivery.json` SUCCEEDED in auditor-run pilot) |

## What is actually connected (working composition)

```text
Goal JSON
  → GoalStore + OrganizationCompiler + MissionAssigner
  → DurableRunner(workflow.sqlite)
       1. gateway_observe  — hardcoded ToolGateway.repo.audit + SqliteDurableGate
       2. achiever_settle  — CTC Execution Brief + Completion Gate (receipts from step 1)
       3. deliver          — delivery.json
  ← gos mission status|pause|resume|cancel|deliver
```

**Auditor reproduction (this session):**

- Command: `gos mission start --goal examples/goal_repo_audit.json --target . --budget-usd 5` under `--root /tmp/gos-audit-pilot`
- Result: `terminal_status=SUCCEEDED`, `completion.status=ACHIEVED`, `tool_calls={"repo.audit":1}`, `llm_used_as_oracle=false`, `production_proven=0`
- Artifact: `PILOT_DELIVERY_SNIPPET.json`
- Automated: `tests/test_preprod_supervised_mission_e2e.py` + CTC + Completion Gate → **30 passed**

## Critical structural finding (P0 product gap)

On the Operator path, **CTC does not select or execute tools**. Tools run in `_gateway_observe_step` before Achiever; Achiever `attempt_fn` only re-injects prior receipts (`world_effects=False`). CTC brief is composed for honesty/routing metadata, not for autonomous tool choice.

Therefore: **implemented approximation ≠ general autonomous OS**.

## Live LLM

| Check | Status |
|-------|--------|
| Model adapters exist in repo | REPORTED (code present) |
| Wired into `runtime/preprod` mission loop | **VERIFIED absent** (no model provider import; only `adapters.storage.sql`) |
| model→tool→observation→verify→next action loop on Operator path | **NOT_TESTED / NOT IMPLEMENTED** |

## Security / durability (summary)

- Capability binding on ToolGateway: **VERIFIED** (code + e2e)  
- HMAC execution tokens + observation attest: **VERIFIED** with **dev secrets by default**  
- Observation HMAC binding action/goal/time: **NOT_CLAIMED_SOLVED** (`delivery.limits`)  
- Crash/resume without silent `repo.audit` replay: **VERIFIED** in automated e2e  
- Temporal for Operator missions: **NOT USED**  
- Secrets/production profile: **PARTIAL** for preprod posture  

## What M-EXT / PREPROD / GE actually showed

| Program | On `main`? | Substance |
|---------|------------|-----------|
| M-EXT1–5 | Historical campaigns in matrix | External science missions; **not** Operator path readiness |
| PREPROD #43/#44 | **Yes** | Supervised repo-audit Operator + CTC v0 |
| Goal Engineering #47 | **Draft PR only** — not on `main` | Deterministic mechanism demo; GE vs verified runbook **NOT SHOWN**; live LLM **NOT_EXECUTED** |

## Open PRs (snapshot)

| PR | Branch | Notes |
|----|--------|-------|
| #47 | `cursor/goal-engineering-study-2907` | Draft, CI green — research; merge optional for preprod |
| #42 | `cursor/perf-audit-opt-2907` | Draft perf — not required for RELEASE_GATE |

## Pre-production readiness

`artifacts/preprod/RELEASE_GATE.md`: **0/10 human-checked**. Auditor assessment of all 10 criteria: see `RELEASE_GATE_ASSESSMENT.md`. None may be marked done solely because CI is green.

## Bottom line for decision makers

1. **Do not declare `v0.1.0-pre`.**  
2. **Do not build new T0/T1 organs** to “feel ready.”  
3. **Next value** is a scoped live (or honest limited) mission that uses the Operator path with real model+tools **or** an explicitly bounded non-LLM expansion of tool choice — see `MINIMAL_PATH_TO_V0_1_PRE.md` / `NEXT_DECISION.md`.
