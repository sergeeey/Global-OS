# M-EXT5 — Mechanical correctness gate

**Status:** `GATE_GREEN`  
**Evidence:** `artifacts/external/EW5_init_mpemba/results/mechanical_gate_results.json`

| # | Check | Status | Evidence |
|---|--------|--------|----------|
| G1 | Confirmatory mode runs | `PASS` | `gate_tests.py` G1 → `run_confirmatory` |
| G2 | N steps = N updates | `PASS` | G2_G4_G5_G6 |
| G3 | Config serializes | `PASS` | G3 |
| G4 | Seed reproducible | `PASS` | G4_repro |
| G5 | Identical batches hot/cold | `PASS` | G2_G4_G5_G6 |
| G6 | Same optimizer/LR | `PASS` | shared Config + SGD |
| G7 | Seal seeds ≠ pilot | `PASS` | pilot 10–14 vs confirmatory ≥1000 |
| G8 | Stats rule consistent (15/20) | `PASS` | `stats_rules.py` + G8 |

All PASS before confirmatory data collection.
