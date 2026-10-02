# M-EXT5 — Reproducibility pack

## Env

- Python 3.12, torch 2.14+cpu, numpy  
- No torchvision required (synthetic data)

## Commands

```bash
cd artifacts/external/EW5_init_mpemba/code
python3 gate_tests.py                 # mechanical gate
python3 run_pilot.py                  # pilot seeds 10–14
python3 run_confirmatory.py           # loads ../../M_EXT5_INIT_MPEMBA_EXAM/SEALED_HOLDOUT.json
```

## Artifacts

- `PREREG.md` / `PREREG.json`  
- `SEALED_HOLDOUT.json`  
- `results/mechanical_gate_results.json`  
- `results/pilot_results.json`  
- `results/confirmatory_results.json`  
- `DECISION.md`  

## Decision rules

See `code/stats_rules.py` — PRIMARY_MIN_WINS=15 for n=20.  
