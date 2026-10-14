# NEXT_DECISION

**For human owners after this audit. Auditor stops here.**

## Do first

1. **Decide Fork A vs Fork B** (`MINIMAL_PATH_TO_V0_1_PRE.md`).  
   - Default recommendation: **Fork A** (narrow supervised preprod) to get an honest `v0.1.0-pre` without waiting on LLM wiring.  
2. **Human-execute RELEASE_GATE** for the chosen profile; do not ask agents to self-certify.  
3. **Keep Challenge-GA NOT_STARTED** until explicit authorize.  
4. **PR #47 (GE)** — merge as research docs or leave draft; **not** on critical path to preprod.  
5. **PR #42 (perf)** — optional; not RELEASE_GATE blocking.

## Do second (only after Fork chosen)

| If Fork A | If Fork B |
|-----------|-----------|
| Clean-env + human delivery review | Authorize budget for live LLM |
| Optional second read-only mission type | Brief→tool registry + model propose loop |
| Tag `v0.1.0-pre` with limits | Then human gate |

## Defer

- Epistemic Kernel deep integration into Operator  
- Temporal for missions  
- Full observation HMAC action/goal/time binding (if staying read-only)  
- Risk Appetite platform / new PDP products  
- Goal Engineering live trials  
- Multi-tenant, Continual SI, PRODUCTION_PROVEN claims  

## Do not build now

| Tempting component | Why not |
|--------------------|---------|
| New T0/T1 kernels | ADR-0009; doesn't close RELEASE_GATE |
| Parallel “AI security product” | Distracts from Operator evidence |
| Challenge-GA “to prove readiness” | Forbidden until authorize; wrong metric |
| PromptKernel / soft LLM security votes | Constitution forbidden pattern |
| Expanding Achiever world effects without Gateway | Authority bypass risk |

## Decision table

| Question | Answer from audit |
|----------|-------------------|
| Can we declare preprod today? | **No** |
| Can operators run a useful bounded mission today? | **Yes** — repo audit pilot |
| Is CI proof of readiness? | **No** |
| Is GE proof of readiness? | **No** (and not on main) |
| First engineering if Fork B? | Connect brief→tool ids→Gateway; then model |
| First work if Fork A? | Human gate ops, not code |

## Auditor terminal

```text
AUDIT_COMPLETE
Pre-production: NOT READY
Next: human decision Fork A/B + RELEASE_GATE
No automatic development started.
```
