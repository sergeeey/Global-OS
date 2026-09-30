# ADR-0012 — T2 selective bounded recovery KEEP (eval harness; no Trust Kernel)

## Status

Accepted — 2026-09-30

## Context

T1 REJECT stood under pack v1 + locked MCID (ADR-0011). Post-T1 diagnostics
classified the failure as `SAFE_CONTAINMENT_BUT_LOW_FAULT_SALVAGE` (benign
incorrectly blocked = 0; fault escapes = 0; useful salvage on recoverable faults
weak). Revival via RT-1/RT-2 on sealed PACK-v2 was preregistered as
`SAFE_AUTONOMY_T2-v1` before unseal.

## Decision

**KEEP** the T2 mechanism under test (selective risk classification + bounded
safe recovery + reverify) as the continued Mission Assurance *eval-harness*
line.

Primary evidence (`artifacts/safe_autonomy_t1/T2/T2_DECISION.md`, experiment SHA
`e6dfd08c0c83e15a25bebc6c8a11a38e48bc0bd3`):

| Arm | MIER | SSR |
|-----|------|-----|
| A | 0.90 | 0.10 |
| B | 0.80 | 0.20 |
| C1 (containment-only) | 0.00 | 0.30 |
| C2 (selective recovery) | 0.00 | 0.80 |

- FSR_C2 = 1.0 (28/28 recoverable salvaged)
- URR_C2 = 0.0 (hard gate)
- HBR_C2 ≈ 0.22 (hard-block classes only)
- T1 REJECT under pack v1 remains immutable

## Consequences

+ H_TRUST line continues under deterministic fault missions with selective recovery.
+ Mechanism frozen as candidate contract `SELECTIVE_BOUNDED_RECOVERY-v1`
  (eval harness only; pin SHA `e6dfd08`).
+ Independent artifact review confirms KEEP (`T2/T2_INDEPENDENT_REVIEW.md`) —
  not an external lab, not a claim upgrade.
+ T3 prereg LOCKED for live-LLM generalization (`T3_PREREG.md`) — **not redesign**.
+ **Still forbidden:** Trust Kernel / T0–T1 core promote; blind verifier weakening;
  T1 MCID rewrite; M1.5 reopen; Y23 IQ-rescue; C2 edit after holdout unseal.
+ Next evidence must not invent production/live-LLM claims from this KEEP alone.
− Live replication (T3) remains required before any stronger trust claim.

## Non-claims

Not production security. Not live-LLM agent superiority. Not Continual SI.
Does not reopen M1.5. Does not overturn T1 REJECT for pack v1.
