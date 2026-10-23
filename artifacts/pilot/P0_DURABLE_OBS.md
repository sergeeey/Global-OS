# P0 — Durable replay gate + observation provenance

> **HISTORICAL:** merged in stack #37–#39 (tip `232022c`); PR #37 merge `36781b5`.
> The “awaiting merge” status below is the pre-merge record, not current state.

**Status:** RUNTIME_VERIFIED_LOCAL (historical; merged in stack #37–#39 @ `232022c`)
**Branch:** `cursor/p0-durable-obs-2907`

## Closed gaps (audit 2026-10-13)

| Gap | Fix |
|-----|-----|
| `_consumed_jti` / idempotency only in RAM | `SqliteDurableGateStore` survives process restart |
| Bare `observation.effect` → WorldSuccess | HMAC attestation + allowlisted source; forged labels rejected |
| Silent Memory / `:memory:` in strict mode | `GOS_REQUIRE_DURABLE_GATE=1` or `GOS_PROFILE=production` fail-closed without on-disk `GOS_DURABLE_GATE_PATH` |

## Adversarial coverage

- Forged `source=gateway_probe` without attestation → DISCREPANCY
- Bogus attestation HMAC → DISCREPANCY
- Strict profile rejects MemoryDurableGateStore and sqlite `:memory:`

## Residual — observation binding / freshness (future)

HMAC currently signs `effect|source|method` only. A valid signature does **not**
yet bind `action_id`, `goal_id`, or observation time — cross-context replay of a
genuine observation remains an open production-audit item. Separate from the two
closed gaps (forged allowlist label; silent RAM-only store).

## Not claimed

- Multi-region distributed lock / consensus
- Hardware/TPM sensor attestation (HMAC shared-secret model only)
- Observation action/goal/time binding (see residual above)
- PRODUCTION_PROVEN
- Challenge exec
- Code on canonical `main` until human merge stack #37→#38→#39
  (see `STACK_MERGE_37_39.md`)

## Code

- `src/global_os/kernel/authority/durable_gate.py`
- `reconcile_effect` / `trusted_observation` in `action_gateway/gateway.py`
- `tests/test_durable_gate_obs_p0.py`
