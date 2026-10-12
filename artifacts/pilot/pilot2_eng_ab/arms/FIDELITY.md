# Fidelity note — PILOT2-ENG-AB-v1 execution

**Status:** `EXECUTED_DUAL_PROTOCOL`  
**Date (UTC):** 2026-10-12  
**Target:** `sergeeey/mcp-bouncer@45af092`

## Constraint

Both arms were executed by the **same cloud-agent executor family** in one session  
(`SAME_EXECUTOR_DUAL_PROTOCOL`). This is **not** independent two-lab replication.

What differs by protocol (binding):

| Dimension | Arm A | Arm B |
|-----------|-------|-------|
| Process | Direct eng audit → findings list | Goal Contract → ledger → repro → claims |
| Artifacts | `ARM_A.md` | `ARM_B_CLAIM_LEDGER.json` + pack |
| Negative retention | optional | required |
| Unsupported claims | often omitted | tallied |
| Independent check | ad hoc | sealed repro pytest pack |

What does **not** differ:

```text
repo pin, tools (local pytest/read), model family, wall session
```

## Implication for H-PILOT2-001

Advantage claims are limited to **protocol/process deltas** under this fidelity.  
Raw “B found more bugs because smarter” is **NOT CLAIMABLE** here.

A future run with separate providers/executors can upgrade fidelity.
