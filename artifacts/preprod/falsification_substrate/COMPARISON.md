# Falsification + Substrate Gate — local comparison

**Branch:** `cursor/verify-falsify-substrate-2907`  
**ADR-0009:** Verification Plane helpers only — no new Kernel / prosecutor agent.  
**Not claimed:** arXiv PoC 100% / 46% token savings (unreproduced here).

## What changed

| Before | After |
|--------|--------|
| Receipt bind + postcondition path match | + active filesystem falsifiers before ACHIEVED |
| Missing expected file → often `unknown` | Expected `FIX_*`/`ACCEPT_*` absent → **falsified → unmet** |
| No substrate vs hypothesis split | `assess_substrate_health` — concrete signals only |
| Bare timeout could be misread as infra | Timeout alone ≠ UNHEALTHY; needs `process_started=False` |

## Fixture outcomes (tests)

| Case | false_success | Notes |
|------|---------------|-------|
| wrong filename (`fix_marker.txt`) | 0 | `criterion_falsified:sc_write` |
| tool success / goal unmet | 0 | receipt RECONCILED overridden by falsifier |
| missing expected file | 0 | falsified unmet |
| exact-line marker mismatch | 0 | `exact_line_marker_absent` |
| corrupted/empty required file | 0 | `required_file_empty` |
| target unavailable | 0 | `ENVIRONMENT_GAP` / substrate UNHEALTHY |
| correct FIX_APPLIED + healthy substrate | allowed SUCCESS | positive control |

Metrics computed in `tests/test_falsification_substrate_gate.py::test_comparison_metrics_fixture_pack`.

## Deferred

- Cross-Model Critic (second family LLM)
- MapReduce research topology
- LLM falsifier for non-concrete criteria
