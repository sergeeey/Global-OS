# R1 decision.md

**Mission:** `R1-EVIDENCE-INTEGRITY-v1`  
**Terminal decision:** `SUPPORTED` (mission objective met)  
**Scientific/universal GOS advantage:** **NOT CLAIMED**

## Hypothesis outcomes

| H | Verdict | Note |
|---|---------|------|
| H1 missing evidence files | REJECTED | 0 broken paths |
| H2 unparseable evidence audit gap | SUPPORTED | 16 RUNTIME_* rows |
| H3 freeze SHA unbound | REJECTED | dir merkle matches; file-hash compare was wrong tool |
| H4 unparseable ⇒ untested overclaim | REJECTED | all 16 had tests |
| H5 path-binding remediation sufficient | SUPPORTED | paths + lint; no downgrades; no T0/T1 |

## What changed

- `docs/capability_matrix.json` — evidence strings now cite existing tests/artifacts/docs
- `tests/test_capability_matrix.py` — `test_capability_evidence_paths_exist`
- Mission trail under `artifacts/r1/`

## What did **not** change

- Y20–Y22 scorers / weights / arms / sealed packs
- Architecture T0/T1
- Maturity states (no silent upgrades; no panic downgrades)

## Operator interventions

**0** recorded.

## Stop

Mission complete. Ready for independent `EVALUATION.md` fill against locked rubric.
