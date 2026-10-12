# Orchestration — Dynamic Tool & Model Orchestration contract

**Organ id:** `orchestration`  
**Status:** `CONTRACT_LOCKED`  
**Job:** bind a ready plan/task to model+tool routing and emit ActionProposals — never bypass Authority / Tool Gateway.

## 1. Input / Output

**In**
- `goal` snapshot
- `plan` + selected `task`
- `routing_context`: cost remaining, latency class, risk, available adapters
- `execution_token` path: Orchestration **proposes**; Authority **decides**

**Out**
- `route_decision`: `{model_tier, tool_ids[], estimated_cost, rationale_code}`
- zero or more typed `ActionProposal` drafts for AuthorityKernel
- `cost_ledger_delta` fields (GOS-I17)

Orchestration does **not** mark Goal success; Verification / Challenge scorer does.

## 2. Authority

- All model calls via `adapters/models/` only.
- All world effects via Tool Gateway with valid ExecutionToken (GOS-I03).
- No LLM boolean security decisions; ConfirmPolicy / Authority remain deterministic gates.
- Capabilities ⊆ Goal / mission grant.

## 3. Quality criteria

| Id | Criterion |
|----|-----------|
| Q-O1 | Every effectful call has proposal → token → receipt path |
| Q-O2 | Cost recorded; overrun → stop route (fail-closed) |
| Q-O3 | ToolSuccess ≠ WorldSuccess; material actions require observation/receipt |
| Q-O4 | Prefer cheaper tier when task class allows (policy table, not vibes) |
| Q-O5 | No hidden provider lock-in; adapter id explicit in ledger |
| Q-O6 | **Purposeful selection:** route records why this tool/model, which alternatives were considered, and stop rule on failure — not “call five tools because we can” |

### Selection mechanism (goal progress)

Orchestration must emit with every ROUTE:

- `why_this_tool` / `why_this_model` (structured codes)  
- `alternatives_considered[]` (may be empty only with explicit `sole_option` reason)  
- `on_failure` → Pivot handoff condition  
- Refusal to expand tool fan-out without criterion-linked justification  

## 4. Error handling

| Condition | Behavior |
|-----------|----------|
| Missing token / DENY | do not call tool; surface to Pivot or stop |
| Effect discrepancy | emit failure to Pivot (not fake success) |
| Provider 429/quota | bounded backoff then fail-closed (existing model HTTP policy) |
| Unknown tool_id | refuse route |
| Cost cap hit | `BUDGET_EXCEEDED` — hand off stop/escalate |

## 5. Control-transfer rules

| From → To | When |
|-----------|------|
| Decomposer → **Orchestration** | Valid plan ready for a runnable task |
| Orchestration → **Authority → Gateway** | ActionProposal for effectful work |
| Orchestration → **Pivot** | Failure, discrepancy, budget pressure, Q-miss |
| Orchestration → **Verifier / Challenge scorer** | Task outputs ready for acceptance checks |
| Orchestration → **stop** | Goal termination / forbidden / budget |
| **Not** Orchestration → rewrite Goal | Forbidden |
| **Not** Orchestration → skip Authority | Forbidden |

## 6. Executable tests

- Contract guards + stub: `tests/test_cognitive_organ_contracts.py`
- Stub: `global_os.cognition.organs.orchestration`
  - produces route decision
  - refuses direct tool execute without token path
  - records cost fields

## Non-claims

```text
≠ live multi-provider optimality proven
≠ Challenge ENG win
≠ PRODUCTION_PROVEN routing
```
