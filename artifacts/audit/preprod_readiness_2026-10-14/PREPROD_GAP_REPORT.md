# PREPROD_GAP_REPORT

**Tip:** `5a7870b` · Gaps block or delay first large live / honest preprod mission.

## P0 — blocks first real large mission (as originally envisioned)

### P0-1 — Operator observe path hardcoded to `repo.audit`

- **Problem:** New Goals cannot choose tools via CTC/Achiever; only the baked-in audit runs.  
- **Evidence:** `supervised_mission.py` `_gateway_observe_step` registers/executes `repo.audit` only; Achiever `attempt_fn` returns prior receipts with `world_effects=False` (≈L185–195, L200+).  
- **Why existing mechanisms insufficient:** CTC + ToolGateway exist but are not linked as Goal→Brief→execute.  
- **Fix check:** Mission for a second Goal type that requires a different registered tool must succeed without editing `_gateway_observe_step` hardcode.  
- **Blocks first large live mission?** **Yes**, if “large” means general tool use beyond repo audit.

### P0-2 — No live LLM closed loop on Operator path

- **Problem:** No model→tool→observation→verify→next-action cycle in preprod runtime.  
- **Evidence:** Preprod imports storage SQL adapter only; CTC/Achiever/Gate explicitly non-LLM; auditor pilot `llm_used_as_oracle=false` with deterministic audit.  
- **Why insufficient:** Adapters elsewhere ≠ wired mission.  
- **Fix check:** Documented mission with provider mock or authorized live call showing ≥2 observe→decide cycles driven by model outputs under Gateway.  
- **Blocks?** **Yes** for LLM-autonomy claims; **No** for declaring a *narrow* non-LLM preprod if product accepts that scope.

### P0-3 — RELEASE_GATE human criteria all unchecked

- **Problem:** Product cannot claim `v0.1.0-pre` while gate is 0/10.  
- **Evidence:** `artifacts/preprod/RELEASE_GATE.md` all ☐; auditor did not mark any done without human.  
- **Fix check:** Human signs each criterion with artifact pointers.  
- **Blocks declaration?** **Yes**.

## P1 — serious for production honesty / second mission

### P1-1 — CTC `allowed_tools` are capabilities, not Gateway tool ids

- **Problem:** Brief grants `filesystem.read` etc.; Gateway tool is `repo.audit` — mismatch invites confusion and future silent bridging.  
- **Evidence:** EnvironmentCompiler `tools.allow = org_caps`; Gateway register tool id `repo.audit`.  
- **Fix check:** Schema that maps capability→tool ids and fails closed on unknown.  
- **Blocks first mission?** Soft for current pilot; **hard** before generalizing tools.

### P1-2 — Semantic criterion binding is substring markers only

- **Problem:** Arbitrary Goal criteria cannot be verified; unsupported stay UNKNOWN (honest) but product looks “broken” for new Goals.  
- **Evidence:** `_REPO_AUDIT_DESC_MARKERS` / excludes in `criteria_supported_by_repo_audit`.  
- **Fix check:** Second mission type with explicit verifier registry entry.  
- **Blocks?** Blocks *general* goals; not the single example Goal.

### P1-3 — Observation HMAC residual (action/goal/time unbound)

- **Problem:** Documented `hmac_action_binding_residual: NOT_CLAIMED_SOLVED`.  
- **Evidence:** `delivery.limits` on auditor pilot; `P0_DURABLE_OBS.md`.  
- **Fix check:** Attestation fails when action_id/goal_id/freshness mismatch.  
- **Blocks first mission?** Not for read-only audit; **yes** before trusting high-impact effects.

### P1-4 — Pause is cooperative between DurableRunner steps

- **Problem:** Long single-step work not interruptible mid-handler.  
- **Evidence:** `_require_control` at step entry.  
- **Fix check:** Document as limit or add cancellation points.  
- **Blocks?** Soft for short audit; hard for long live runs.

### P1-5 — Default DEV HMAC secrets in Operator path

- **Problem:** Preprod convenience ≠ production secret posture.  
- **Evidence:** ExecutionToken / observation keys fall back to DEV constants unless env set.  
- **Fix check:** Fail-closed when secrets unset under a supervised “hard” profile.  
- **Blocks?** Soft for local; hard for shared/hosted preprod.

## P2 — polish / non-blocking for scoped pilot

| ID | Gap | Notes |
|----|-----|-------|
| P2-1 | Only one example Goal | `examples/goal_repo_audit.json` |
| P2-2 | Temporal unused on Operator | Optional later |
| P2-3 | OTEL not required on pilot | Optional |
| P2-4 | GE / perf draft PRs | Not on critical path to RELEASE_GATE |
| P2-5 | Epistemic Kernel not in Operator composition | Can stay library-level for v0.1-pre |

## Explicit non-gaps (already addressed for pilot)

- Mid-progress / empty receipts ≠ SUCCESS — e2e VERIFIED  
- Corrupt/empty/discrepancy/tool failure ≠ SUCCEEDED — e2e VERIFIED  
- Bare `sc_01` without semantic match ≠ ACHIEVED — e2e VERIFIED  
- Empty CTC allowed_tools ≠ invent filesystem.read — VERIFIED  
- Challenge-GA correctly NOT_STARTED — honesty intact  

## Counterexamples sought

| Attempt | Result |
|---------|--------|
| Claim CTC executes tools on Operator | **Counterexample found** — hardcoded observe |
| Claim live LLM on Operator | **Counterexample found** — no provider loop |
| Claim false SUCCESS via empty receipts | **Blocked** by Gate (tests) |
| Claim PRODUCTION_PROVEN | **Denied** by delivery honesty + matrix |
