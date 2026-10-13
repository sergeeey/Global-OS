# P0 — Durable replay gate + observation provenance

**Status:** RUNTIME_VERIFIED_LOCAL (tip branch; awaiting human merge stack)  
**Branch:** `cursor/p0-durable-obs-2907`

## Closed gaps (audit 2026-10-13)

| Gap | Fix |
|-----|-----|
| `_consumed_jti` / idempotency only in RAM | `SqliteDurableGateStore` survives process restart |
| Bare `observation.effect` → WorldSuccess | Requires trusted `source`+`method`; else DISCREPANCY |

## Not claimed

- Multi-region distributed lock / consensus
- PRODUCTION_PROVEN
- Challenge exec

## Code

- `src/global_os/kernel/authority/durable_gate.py`
- `reconcile_effect` / `trusted_observation` in `action_gateway/gateway.py`
- `tests/test_durable_gate_obs_p0.py`
