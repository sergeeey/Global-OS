# ADR-0010 — M1.4 Trust Boundary Hardening

**Status:** Accepted  
**Date:** 2026-09-22

## Context

Empirical dogfood (Y17-1..5) proved research missions run, but audit showed trust
boundaries incomplete: opaque execution tokens, raw bearer in ledger, approval_id
string bypass, mutable claim_id overwrite, epistemic RAM-only graph, and
ToolSuccess treated too close to WorldSuccess. Running 48h before closing these
would validate durability of an incomplete authority/epistemic surface.

## Decision

Insert milestone **M1.4 — Trust Boundary Hardening** before M1.5:

1. Proposal-bound `ExecutionToken` (proposal_hash, identity, capability, resource,
   goal/version, expiry, one-time jti); Gateway verifies binding.
2. Event Ledger stores `execution_token_id` / `execution_token_hash` only — never
   raw bearer.
3. `ApprovalService.verify_and_consume()` on Authority path; approval_id string alone
   insufficient.
4. Immutable insert for claims/evidence (new id for new version).
5. Cold-restart epistemic reconstruction from durable ledger snapshot.
6. Effect reconciliation states: EXECUTED → OBSERVATION_PENDING → RECONCILED |
   DISCREPANCY → ESCALATION_REQUIRED (GOS-I13 enforced).

M1.5 remains Long-Horizon Reality Validation (live IV + 48h persistent research
program + Goal Integrity). Preference Ledger / VOI / learned org compiler stay out
of scope until after M1.4/M1.5 evidence.

## Consequences

- Dogfood order becomes: CI green → M1.4 P0 → local provider IV → Y17-6/7 + Org N↑
  → 48h → only then M1.5 claim.
- ADR-0009 empirical freeze remains: no new T0/T1 fantasy subsystems beyond these
  invariant-required trust fixes.
