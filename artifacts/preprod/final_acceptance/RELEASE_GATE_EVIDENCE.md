# RELEASE_GATE_EVIDENCE

Maps `PREPROD_RELEASE_GATE.md` / `RELEASE_GATE.md` criteria to proof.

| # | Evidence pointer |
|---|------------------|
| 1 | `artifacts/preprod/OPERATOR.md` install section |
| 2 | CLI `gos mission start`; e2e `test_supervised_mission_end_to_end_delivery` |
| 3 | e2e pause/cancel; budget insufficient negative |
| 4 | `scripts/preprod_real_kill_recovery.py` + `recovery/REAL_KILL_RECOVERY.json` |
| 5 | Same + crash-resume e2e tool_calls==1 |
| 6 | `missions/se_delivery.json`, `missions_live/se_delivery.json` |
| 7 | `missions/research_delivery.json`, `missions_live/research_delivery.json` |
| 8 | Negatives in `tests/test_preprod_supervised_mission_e2e.py` |
| 9 | delivery.json fields: budget, model_*, effect_receipts |
| 10 | Fork B fix + catalog fail-closed; see INTEGRATION_EVIDENCE |

Human checkboxes remain open by design.
