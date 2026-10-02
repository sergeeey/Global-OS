# M-EXT5 — Mechanical correctness gate

**Status:** `GATE_OPEN_ALL_PENDING`  
**Rule:** No pilot scientific claims and **no confirmatory data collection** until every row is `PASS` with evidence path.

| # | Check | Status | Evidence |
|---|--------|--------|----------|
| G1 | Confirmatory mode actually runs (loads seal, executes pairs, writes results) | `PENDING` | |
| G2 | “N SGD steps” means exactly N parameter updates (not epochs-miscounted) | `PENDING` | |
| G3 | Full config serializes to JSON (bit-reproducible fields recorded) | `PENDING` | |
| G4 | Seed reproducibility: same seed ⇒ same init + same batch sequence | `PENDING` | |
| G5 | Hot/cold receive **identical** batches (paired) | `PENDING` | |
| G6 | Optimizer / LR / noise process identical across hot/cold | `PENDING` | |
| G7 | Sealed confirmatory seeds unread during pilot / gate work | `PENDING` | |
| G8 | Statistical decision rules internally consistent (threshold ↔ stated α/test) | `PENDING` | |

## Notes

- M-EXT4 code must **not** be assumed to pass G1/G8 (see M-EXT4 ERRATA E4/E5).  
- Prefer a clean M-EXT5 package under `artifacts/external/EW5_init_mpemba/` rather than silently patching M-EXT4 history.  
- When all PASS, set this file status to `GATE_GREEN` and record SHA of gate evidence in `MISSION_LEDGER.json`.
