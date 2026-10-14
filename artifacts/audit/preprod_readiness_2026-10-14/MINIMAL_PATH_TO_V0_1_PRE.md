# MINIMAL_PATH_TO_V0_1_PRE

Shortest practical path to a **limited** `v0.1.0-pre` — not to Continual SI or Challenge-GA.

## Product decision fork (choose one)

### Fork A — Narrow preprod (recommended minimum)

**Declare profile:** `PREPROD_SUPERVISED` = one operator, one mission, **read-only repo audit** (or similarly bounded deterministic tools), no LLM required.

| Step | Action | Closes | Verify |
|------|--------|--------|--------|
| A1 | Human clean-env install from OPERATOR.md on fresh machine | Gate 1 | Screenshot + `gos mission start` log |
| A2 | Human runs example Goal; reviews `delivery.json` findings | Gate 2,6,9 | Independent notes on report quality |
| A3 | Human exercises pause/cancel/resume + crash-resume script | Gate 3,4,5 | Match e2e expectations |
| A4 | Document honest limit: second mission type **deferred** OR add one second **read-only** tool+Goal+verifier | Gate 7 | Delivery for type B or LIMITS.md |
| A5 | Freeze launch profile listing allowed tools + DEV-secret warning | Gate 10 | No open P0 **inside** that profile |
| A6 | Human marks RELEASE_GATE; tag `v0.1.0-pre` with profile text | Declaration | Tag message cites SHA + limits |

**Do not build:** new organs, Risk Engine product, PromptKernel, Challenge-GA, Temporal rewrite.

### Fork B — LLM-assisted preprod (larger)

Only if product insists on “real LLM organizes execution”:

| Step | Action | Closes |
|------|--------|--------|
| B0 | All of Fork A honesty scaffolding | Baseline |
| B1 | Wire **one** model adapter into Operator under ToolGateway (no direct world effects from model) | P0-2 |
| B2 | Replace hardcoded observe with brief→allowed tool ids registry (still capability-subset) | P0-1, P1-1 |
| B3 | Cap attempts/budget; keep Completion Gate non-LLM | False SUCCESS |
| B4 | One authorized live coding/research mission with independent human verify | Gate 2,6,7 |
| B5 | Measure $/latency; seal audit trail | Gate 9 |

B1–B4 are **development**, not audit. Require separate human authorize (cost + scope).

## What is explicitly out of minimal path

- Challenge-GA execution  
- New T0/T1 architecture  
- Full HMAC residual closure (can stay documented limit for read-only)  
- GE live A/B  
- Multi-tenant SaaS  
- Production `GOS_PROFILE=production` without rust Authority + real secrets  

## Minimal engineering if Fork A chosen

**Zero** mandatory code changes if humans accept single-mission-type limit.  
Optional small docs: `LIMITS.md` stating CTC does not drive tools yet.

## Minimal engineering if Fork B chosen

Order: tool registry from brief → model propose tools only → Gateway execute → Gate verify.  
Reuse existing Authority/Gateway/Gate; do not invent parallel security.
