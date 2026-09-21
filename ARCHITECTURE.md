# ARCHITECTURE.md

## Style

Logical microkernel / modular monolith + few hard-isolated security services.

```text
Python Runtime
 ├ Goal / Epistemic / Organization / Verification / Memory / Model adapters

Rust Authority Service (target; Python stub until Sprint 2 hardens)
 ├ authorization · capability · action normalization · approvals · effect protocol

Temporal — durable workflows
PostgreSQL — canonical structured state
Object Store — artifacts
Sandbox Runner — untrusted execution
Web Console — UX (deferred past CLI/API)
```

## Control flow

```text
HUMAN / ORG
    → GOAL CONTRACT
    → AUTHORITY KERNEL (identity / budgets / approvals / invariants)
    → COGNITIVE RUNTIME (Metareasoner · OrgCompiler · ModelRouter · Workers)
         ├ EPISTEMIC KERNEL (evidence · claims · hypotheses · models)
         └ WORLD STATE (observed · believed · expected · committed)
    → VERIFICATION PLANE
    → ACTION PROPOSAL
    → AUTHORITY KERNEL
    → WORLD INTERACTION (tool gateway · sandbox)
    → EFFECT RECEIPT
    → EVENT LEDGER
    → REPLAY / ADAPTATION
```

## Stability principle

Stable: contracts and invariants.  
Replaceable: models, MCP, A2A, vector DB, Temporal, k8s.

## Packages (monorepo)

See repository tree in root. Logical modules under:

- `contracts/` — schemas, OpenAPI, events, versions  
- `kernel/` — authority, identity, policy, action_gateway  
- `runtime/` — goals, workflows, scheduler, events, recovery, replay  
- `cognition/` — metareasoning, organization, workers, model_router  
- `epistemic/` — observations, claims, evidence, invalidation, provenance  
- `memory/` — episodic, semantic, procedural, decision, negative, counterfactual, preference, authorization  
- `verification/` — router + protocol implementations  
- `world/` — tools, sandbox, mcp, effects  
- `adaptation/` — proposals, experiments, promotion  
- `adapters/` — models, tools, identity, sandbox, storage  
- `apps/` — api, console  
- `evals/` — survival, epistemic, authority, organization  

## Event sourcing (selective)

Append-only for: goal amendments, authority changes, task transitions, action proposals, authz decisions, approvals, external actions, effect receipts, evidence invalidation, procedure promotions.

State views = projections.

## Trust zones

T0 Constitutional Core (no self-mod) → T1 Trusted Runtime → T2 Adaptive Procedures → T3 Experiments.
