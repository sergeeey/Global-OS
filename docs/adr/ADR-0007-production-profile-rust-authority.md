# docs/adr/ADR-0007-production-profile-rust-authority.md

## Context

Rust Authority process boundary exists (`gos-authority`), but default remains Python for local/tests.
Ops need a production profile that prefers the process boundary without silent downgrade.

## Problem

How to default production to Rust Authority while keeping CI/dev ergonomic?

## Alternatives

1. Always default Rust globally (breaks environments without the binary)  
2. Document-only recommendation  
3. Explicit `GOS_PROFILE=production` → rust + startup probe, fail-closed (chosen)

## Decision

- `GOS_PROFILE=dev|production` (default `dev`)  
- Production defaults `GOS_AUTHORITY_BACKEND=rust` and probes `gos-authority` at `RuntimeContext` init  
- Production + python backend is rejected  
- Missing binary → `ProductionProfileError` (never silent Python allow)

## Evidence

`tests/test_runtime_profile.py`

## Trade-offs

+ Honest production posture  
− Operators must ship `gos-authority` before enabling production profile
