# PREPROD_V0_1 — Integration-gap audit (main @ branch cut)

**Stage:** `PREPROD_V0_1` (supervised Operator Edition)  
**Baseline tip at audit start:** `2e9d485`  
**Challenge-GA:** `NOT_STARTED` (no authorize)  
**PRODUCTION_PROVEN:** `0`  
**CONTINUAL_SI:** `NOT_MEASURED`

## Intent

Stop building new intellectual organs. Assemble existing mechanisms into one
userable user path: Goal → autonomous work in bounds → recovery → operator
control → verified delivery.

## Capability matrix (gap)

| Capability | Entrypoint | Code | Test | Gap (before PREPROD_V0_1) | Severity |
|---|---|---|---|---|---|
| Mission launch | `gos goal create` only | `cli.py`, `GoalStore` | `test_goal_and_events` | No mission start | **P0** |
| Autonomous execution | library Achiever | `achiever_loop.py` | injected receipts | No CLI attempt via Gateway | **P0** |
| Operator control | `goal show` / `events` | Confirm/Approval libs | policy tests | No pause/resume/cancel | **P0** |
| Durable recovery | DurableRunner harness | `durable.py`, kill harness | `test_durable_recovery` | Not wired to user mission | **P1** |
| Live model + tools | adapters + Gateway | eval harnesses | live optional | No default mission tool loop | **P0** |
| Verification | Completion Gate | `completion_gate.py` | adversarial tests | Not on operator path | **P1** |
| Delivery | events / audit dump | ArtifactStore | e2e repo audit | No delivery package | **P0** |

## What this stage added (composition only)

No new Authority / Verification / scheduler / UI framework.

| Piece | Location |
|-------|----------|
| Supervised runner | `src/global_os/runtime/preprod/supervised_mission.py` |
| CLI | `gos mission start\|status\|pause\|resume\|cancel\|deliver` |
| E2E acceptance | `tests/test_preprod_supervised_mission_e2e.py` |
| Operator guide | `artifacts/preprod/OPERATOR.md` |

Path composed: GoalStore → OrganizationCompiler → MissionAssigner → DurableRunner →
ToolGateway(`repo.audit` read-only) + SqliteDurableGate → Achiever control settle →
Completion Gate → `delivery.json`.

## Honesty boundaries

- Profile label `PREPROD_SUPERVISED` is **mission metadata**, not a new `GOS_PROFILE` enum.
- First mission tool is **read-only** `repo.audit` (sandbox). External write / PR still requires human confirmation (not automated).
- HMAC action_id/goal_id/freshness residual: **NOT claimed solved** (documented in delivery.limits).
- Live multi-hour LLM coding missions: **not** claimed by this e2e.
- Mid-progress ≠ SUCCESS enforced by Completion Gate (empty receipts ≠ ACHIEVED).
- **P0 fix:** never blanket `criterion_checks=True` from non-empty receipts; attest observation only after independent `verify_repo_audit_report`; negative e2e covers DISCREPANCY / corrupt / empty / partial / budget.
- **P0 fix:** `repo.audit` binds only `criteria_supported_by_repo_audit` (never all Goal criteria); unrelated criteria stay UNKNOWN (e2e without override).
- Challenge-GA remains NOT_STARTED.

## Release gate (manual checklist — 0/10 until human marks)

See `artifacts/preprod/RELEASE_GATE.md`.
