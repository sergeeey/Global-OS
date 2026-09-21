# docs/adr/ADR-0006-strong-sandbox-fail-closed.md

## Context

Execution environments may request `sandbox.profile: container|gvisor|microvm`.
Risk: silently running untrusted code in `process_local` while claiming strong isolation.

## Problem

How to ship a strong-sandbox port without Docker/gVisor in every environment?

## Alternatives

1. Always require Docker+gVisor in CI from day one  
2. Silent fallback from `container` → `process_local`  
3. Fail-closed factory + optional live Docker harness (chosen)

## Decision

- `open_sandbox("container")` probes Docker and raises `StrongSandboxUnavailable` if missing  
- `gvisor` / `microvm` raise until implemented — never silent downgrade  
- `process_local` remains the MVP path (`sandbox_mvp`)  
- Live container isolation is claimed only when Docker harness evidence exists

## Evidence

`tests/test_sandbox.py`: fail-closed without Docker; optional live container test when daemon present.

## Trade-offs

+ Honest isolation claims  
− Strong profiles blocked without container runtime

## Reversal trigger

Claim `sandbox_strong` as RUNTIME_VERIFIED_HARNESS only after CI regularly exercises Docker (or gVisor) isolation.
