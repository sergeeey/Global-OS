# ADR-0011 — T1 thin Mission Assurance REJECT (no Trust Kernel promote)

## Status

Accepted — 2026-09-30

## Context

Post-M1.5 SAFE_AUTONOMY_BENCHMARK-v1 ran T1 A/B/C under
`DETERMINISTIC_FAULT_MISSIONS_v1` with locked MCID from variance pilot.

## Decision

**REJECT** integration of thin Mission Assurance into Trust Kernel / T0–T1.

Primary evidence (`artifacts/safe_autonomy_t1/T1_DECISION.md`):

- MIER_C = 0.0 < MIER_A = 0.9 and MIER_B = 0.8 (integrity escapes down)
- SSR_C = 0.3 best among arms
- KEEP failed on frozen reason `verifier_tax_2_0_completion`
  (completion_rate A=1.0 → C=0.3 exceeds utility_tax_max=0.15)

## Consequences

+ H_TRUST **not confirmed** in tested scope; mechanism shows escape reduction with unacceptable completion tax under this pack.
+ No silent T0/T1 promotion of Mission Assurance / MI-1..5.
+ No MCID rewrite; no Y23/IQ-rescue.
− Future work must either redesign thin MA for lower overblocking, change experiment class with new prereg, or pursue other trust mechanisms — not celebrate MIER-alone.

## Non-claims

Does not reopen M1.5. Does not prove live-LLM results. Does not prove production security.
