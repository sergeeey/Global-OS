# CAPABILITY_EVIDENCE_MATRIX

**Tip:** `5a7870b` · **Statuses:** `VERIFIED` | `REPORTED` | `PARTIAL` | `NOT_TESTED` | `BROKEN` | `UNKNOWN`

| Claimed capability | Code locus | Test / runtime evidence | Status | Notes |
|--------------------|------------|-------------------------|--------|-------|
| GoalContract immutable/versioned | `contracts/schemas/goal_contract.schema.json`, GoalStore | `tests/test_goal_and_events.py` | VERIFIED | Schema enforced |
| Operator mission CLI | `cli.py` mission_*; `supervised_mission.py` | e2e + auditor CLI pilot | VERIFIED | start/status/pause/resume/cancel/deliver |
| Goal → Mission assignment | OrgCompiler + MissionAssigner in `start_mission` | e2e | VERIFIED | Manager-workers compile |
| ToolGateway capability bind | `gateway.py` register/execute | e2e observe | VERIFIED | `filesystem.read` required for `repo.audit` |
| Durable SQLite workflow | `DurableRunner` + `workflow.sqlite` | `test_crash_resume_*` | VERIFIED | Not Temporal |
| Idempotent tool replay block | `SqliteDurableGate` + stable key | crash e2e call_count==1 | VERIFIED | For this tool key only |
| CTC Execution Brief | `task_compiler.py` / Achiever | `test_contextual_task_compiler.py` | VERIFIED | Deterministic; no model |
| CTC drives tool selection on Operator | — | code inspection | **PARTIAL / gap** | Observe hardcoded; Achiever passthrough |
| Empty allowed_tools fail-closed | `achiever_loop.py` | CTC test | VERIFIED | No implicit filesystem.read |
| Completion Gate ACHIEVED honesty | `completion_gate.py` | many negative e2e | VERIFIED | No LLM oracle; no bare tool_success |
| Semantic criterion bind (repo audit) | `criteria_supported_by_repo_audit` | sc_01 / unrelated e2e | VERIFIED | Substring markers; not general NLU |
| Delivery package | `_deliver_step` → `delivery.json` | e2e + auditor pilot | VERIFIED | Honesty flags present |
| Live LLM in Operator loop | `adapters/models/*` unused by preprod | import scan | **NOT_TESTED** (absent) | Adapter≠mission |
| General multi-step planning for new goals | Decomposer/Orchestration stubs | organ tests | PARTIAL | Deterministic; not open-ended |
| Epistemic Kernel on Operator path | epistemic modules exist | not invoked in supervised path | PARTIAL | Not composition-critical for pilot |
| Temporal durability for missions | `TemporalBridge` elsewhere | — | NOT_TESTED | Unused by Operator |
| HMAC action/goal/time obs bind | residual documented | delivery.limits | PARTIAL | NOT_CLAIMED_SOLVED |
| Production secrets posture | `GOS_*_SECRET` / profile | default DEV keys | PARTIAL | Preprod uses dev defaults |
| External write / PR automation | limits.external_write | — | NOT_TESTED | human_confirmation_required |
| Challenge-GA | challenge_ga harness | — | NOT_TESTED | NOT_STARTED |
| False SUCCESS via empty receipts | Completion Gate | e2e mid-progress | VERIFIED blocked |
| False SUCCESS via corrupt/empty audit | verify before attest | negative e2e | VERIFIED blocked |
| False SUCCESS via unrelated criterion | semantic support set | e2e | VERIFIED blocked |
| Clean-env deploy from empty machine | OPERATOR.md | auditor used existing env | PARTIAL | Docs exist; full clean VM NOT_TESTED this audit |
| Spend / budget in delivery | budget fields | pilot spent_usd=0.01 | VERIFIED | Simulated tool cost |
| Observability (OTEL) on Operator | otel optional | — | UNKNOWN | Not required by pilot path |
| GE superiority (PR #47) | not on main | draft PR | N/A on tip | Mechanism demo only if merged |

## Matrix vs `docs/capability_matrix.json`

| Matrix id | Matrix state | Auditor agreement |
|-----------|--------------|-------------------|
| `preprod_supervised_mission_v0` | RUNTIME_VERIFIED_LOCAL | **Agree** for pilot scope; ≠ general autonomy |
| `contextual_task_compiler_v0` | RUNTIME_VERIFIED_LOCAL | **Agree** as compiler; **Disagree** if read as “drives Operator tools” |
| `achiever_organ_loop_contour_a` | RUNTIME_VERIFIED_LOCAL | **Agree** (control contour; no world effects) |
| `goal_completion_gate` | RUNTIME_VERIFIED_LOCAL | **Agree** |
| Any PRODUCTION_PROVEN | 0 | **Agree** |
