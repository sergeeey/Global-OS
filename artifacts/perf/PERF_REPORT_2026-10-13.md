# Performance audit & optimization — 2026-10-13

**Branch:** `cursor/perf-audit-opt-2907`  
**Baseline tip:** `2e9d485` (`main` at branch cut)  
**Harness:** `PYTHONPATH=src python3 tools/perf_bench.py`  
**Artifacts:** `artifacts/perf/baseline_pre_opt.json`, `artifacts/perf/after_opt.json`

## Scope

Hot-path microbenchmarks for core runtime (not end-to-end LLM missions):

| Path | Why |
|------|-----|
| `content_hash` | Every ledger append / token bind |
| `validate(event/receipt)` | Contract gate on critical paths |
| `EventLedger.append` / `list_events` | Epistemic + gateway event volume |
| `ExecutionToken` mint+consume | Authority hot path |
| `SqliteDurableGate` claim+put+get | P0 durable replay gate |
| `completion_gate` | Contour A terminal check |

**Non-goals:** model/provider latency, Temporal cluster, network I/O, Challenge-GA exec.

**Interface rule:** public call signatures unchanged; behavior preserved (isolation of returned event copies; schema validation still rejects invalid instances).

## Bottlenecks found (baseline)

| Hot path | µs/op (baseline) | Diagnosis |
|----------|------------------|-----------|
| `durable_gate_claim_put_get` | **2568** | SQLite default `synchronous=FULL` + WAL; 3 commits/op |
| `ledger_list_events_200` | **756** | `copy.deepcopy` of 200 JSON events |
| `ledger_append` | **74** | hash + new `Draft202012Validator` + deepcopy return |
| `validate_*` | **47–50** | Validator reconstructed every call |
| `content_hash` / `completion_gate` | **3–11** | Already cheap |

## Optimizations (no API breaks)

1. **Cache compiled JSON Schema validators** — `contracts/validate.py` `_validator_for` + `lru_cache`
2. **`jsonable_copy`** — recursive copy for JSON-shaped trees; used by `EventLedger` append/list/from_snapshot and `SqlEventLedger.append`
3. **SQLite durability profile** — `PRAGMA synchronous=NORMAL` + `temp_store=MEMORY` on `SqliteDurableGateStore`; same WAL+NORMAL on on-disk `connect_sqlite`

Durability note: `NORMAL` with WAL remains process-crash safe for jti/idempotency; it is not a claim of battery-backed FULL fsync semantics. Documented in code comments.

## Measurements (reproducible)

Environment recorded in JSON `meta` (Python 3.12, Linux).

### Composite (weighted micro mix)

| | weighted_cost_s | vs baseline |
|--|-----------------|-------------|
| Baseline | 0.066574 | — |
| After | 0.008999 | **86.5% faster (7.40×)** |

Weights (see harness): ledger_append×40, durable×20, list×15, validate×15, token×5, gate×3, hash×2.

> Composite is dominated by the durable-gate fix. Per-path table is the honest breakdown.

### Per-path

| Bench | Baseline µs | After µs | Improvement |
|-------|------------:|---------:|------------:|
| durable_gate_claim_put_get | 2568.0 | 77.4 | **97.0%** |
| ledger_list_events_200 | 755.8 | 280.5 | **62.9%** |
| ledger_append | 74.3 | 60.4 | **18.7%** |
| validate_effect_receipt | 50.5 | 43.9 | **13.1%** |
| validate_event | 47.2 | 41.7 | **11.6%** |
| content_hash | 10.7 | 10.7 | ~0% |
| execution_token_mint_consume | 33.5 | 34.4 | noise |
| completion_gate | 3.1 | 3.1 | ~0% |

**Excluding durable_gate from the weighted mix**, remaining hot paths improve ~**35%** (ledger list + append + validate dominate).

## Reproduce

```bash
# from repo root, same machine class
PYTHONPATH=src python3 tools/perf_bench.py --out /tmp/gos_perf.json
PYTHONPATH=src python3 tools/perf_bench.py \
  --compare artifacts/perf/baseline_pre_opt.json \
  --out /tmp/gos_perf_cmp.json
```

Regression guards: `tests/test_perf_jsonable_ledger.py` (isolation + validator still rejects bad events).

## Honesty

- Microbench ≠ production mission wall-clock.
- Not PRODUCTION_PROVEN throughput.
- Challenge-GA / Continual SI unchanged / not started.
- No public interface removals or schema changes.

## Status

```
Perf audit              DONE
Benchmarks              tools/perf_bench.py + artifacts/perf/*.json
Opt progress            >30% (composite 86%; non-sqlite mix ~35%)
Interfaces              UNCHANGED
pytest                  449 passed / 12 skipped (local)
```
