# Performance audit & optimization — 2026-10-13

**Branch:** `cursor/perf-audit-opt-2907`  
**Baseline tip:** `2e9d485` (`main` at branch cut)  
**Harness:** `PYTHONPATH=src python3 tools/perf_bench.py`  
**Artifacts:** `artifacts/perf/baseline_pre_opt.json`, `artifacts/perf/after_opt.json`

## Durability decision (merge blocker resolved)

Review feedback on PR #42: weakening `PRAGMA synchronous` from **FULL → NORMAL** on the
Authority durable gate (jti / idempotency) trades power-loss durability for speed and can
allow **replay of an already-executed external action** after OS/power failure.

**Policy now:**

| Store | `synchronous` | Rationale |
|-------|---------------|-----------|
| `SqliteDurableGateStore` (jti, idempotency) | **FULL** (mandatory) | Authority Kernel — lost commit ⇒ double execution |
| `connect_sqlite(...)` default (event / action journal) | **FULL** | Journal of executed actions is recovery-critical |
| `connect_sqlite(..., synchronous="NORMAL")` | NORMAL (opt-in) | Rebuildable caches/projections only |

Regression guards: `tests/test_perf_jsonable_ledger.py`
(`test_durable_gate_keeps_full_synchronous`, `test_connect_sqlite_defaults_to_full_synchronous`).

An earlier draft of this PR used NORMAL on the durable gate for a ~7× composite score.
**That figure is withdrawn** as a merge metric; it depended on an unacceptable durability trade-off.

## Scope

Hot-path microbenchmarks for core runtime (not end-to-end LLM missions):

| Path | Why |
|------|-----|
| `content_hash` | Every ledger append / token bind |
| `validate(event/receipt)` | Contract gate on critical paths |
| `EventLedger.append` / `list_events` | Epistemic + gateway event volume |
| `ExecutionToken` mint+consume | Authority hot path |
| `SqliteDurableGate` claim+put+get | P0 durable replay gate (**FULL sync**) |
| `completion_gate` | Contour A terminal check |

**Non-goals:** model/provider latency, Temporal cluster, network I/O, Challenge-GA exec.

**Interface rule:** public call signatures unchanged (additive kw-only `synchronous=` on
`connect_sqlite`); schema validation / event isolation preserved.

## Optimizations kept (durability-preserving)

1. **Cache compiled JSON Schema validators** — `contracts/validate.py`
2. **`jsonable_copy`** — ledger / SQL event return isolation without `deepcopy`
3. **Opt-in NORMAL** only via `connect_sqlite(..., synchronous="NORMAL")` for rebuildable stores

## Measurements (reproducible)

### Headline: durability-preserving score

| Metric | Baseline | After | Change |
|--------|----------|-------|--------|
| `_composite_safe` (excludes durable gate) | 0.015214 | 0.007386 | **+51.5% (2.06×)** |
| `_composite` (includes durable FULL) | 0.066574 | 0.068190 | ~noise (−2.4%) |

Durable gate intentionally stays FULL; including it in the mix **must not** be “won” by
weakening sync. Use `_composite_safe` as the optimization KPI.

### Per-path

| Bench | Baseline µs | After µs | Improvement |
|-------|------------:|---------:|------------:|
| ledger_list_events_200 | 755.8 | 279.6 | **63.0%** |
| ledger_append | 74.3 | 59.8 | **19.5%** |
| validate_event | 47.2 | 40.0 | **15.3%** |
| validate_effect_receipt | 50.5 | 44.6 | **11.7%** |
| content_hash | 10.7 | 10.7 | ~0% |
| execution_token_mint_consume | 33.5 | 34.1 | noise |
| completion_gate | 3.1 | 3.1 | ~0% |
| durable_gate_claim_put_get | 2568 | ~3040 | noise / FULL preserved (not optimized via NORMAL) |

## Reproduce

```bash
PYTHONPATH=src python3 tools/perf_bench.py \
  --compare artifacts/perf/baseline_pre_opt.json \
  --out artifacts/perf/after_opt.json
# or: make perf-bench
```

## Honesty

- Microbench ≠ production mission wall-clock; not an “OS is 7× faster” claim.
- Withdrawn: composite 7.4× that relied on `synchronous=NORMAL` for authority.
- Not PRODUCTION_PROVEN throughput. Challenge-GA unchanged / NOT_STARTED.

## Status

```
Perf audit                 DONE
Durability policy          FULL for authority + default event journal
Safe-path improvement      ~51% (_composite_safe)
NORMAL                     opt-in only for rebuildable caches
Interfaces                 UNCHANGED (additive connect_sqlite kw)
Challenge-GA               NOT_STARTED
```
