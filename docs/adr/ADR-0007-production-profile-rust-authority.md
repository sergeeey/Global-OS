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
- Production requires `GOS_EXECUTION_TOKEN_SECRET` and `GOS_APPROVAL_SIGNING_SECRET`
  (non-empty, not known dev defaults) — AUTH-002
- Production `ToolGateway(allow_legacy_tokens=False)` — opaque `accept_token`
  deposit path forbidden (AUTH-001)

## Evidence

`tests/test_runtime_profile.py`

## Trade-offs

+ Honest production posture  
− Operators must ship `gos-authority` and real HMAC secrets before enabling production profile
