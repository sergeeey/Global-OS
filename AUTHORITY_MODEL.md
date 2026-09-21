# AUTHORITY_MODEL.md

## Principle

Intelligence proposes; Authority decides; Gateway executes only with a token.

## ActionProposal (normalized)

Required fields: principal, goal, capability, resource, intended_effect, maximum_effect, reversible, information_disclosure, monetary_cost, idempotency_key, evidence_refs, approval_refs, context.

## Decision

`ALLOW` | `DENY` | `PENDING_APPROVAL`

## Capability model

Fine-grained capabilities (`web.read`, `email.draft`, `email.send`, …).  
No `everything`, `admin`, or `Bash(*)` for cognitive workers.

## Inheritance

$$
Authority(child) \subseteq Authority(parent)
$$

Parent request cannot expand child beyond parent's grant.

## Approvals

Signed/versioned; bound to `action_hash`, goal, limits, `valid_until`, optionally one-time.  
Not reusable across different action hashes.

## Proof-Carrying Action (material)

Action + goal authorization + capability + budget + evidence + approvals + expected effect + verification plan + rollback/reconciliation plan.

## Effect Contract / Receipt

Before: expected effect + observation method + timeout.  
After: tool_response vs intended vs observed + discrepancy.  
Without reconciliation, high-impact action is not `COMPLETED`.

## Kernel boundary

Authority Kernel must not call models.  
Policies: Cedar (principal / action / resource / context), default-deny.
