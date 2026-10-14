# RELEASE_GATE_EVIDENCE

Maps `PREPROD_RELEASE_GATE.md` / `RELEASE_GATE.md` criteria to proof.

| # | Evidence pointer |
|---|------------------|
| 1 | `artifacts/preprod/OPERATOR.md` + `CLEAN_INSTALL.md` / `CLEAN_INSTALL_PROOF.json` |
| 2 | CLI `gos mission start`; e2e `test_supervised_mission_end_to_end_delivery` |
| 3 | e2e pause/cancel; budget insufficient negative |
| 4 | `scripts/preprod_real_kill_recovery.py` + `recovery/REAL_KILL_RECOVERY.json` |
| 5 | Same + `preprod_crash_window_recovery.py` + `CRASH_WINDOW_RECOVERY.json` |
| 6 | `missions/se_delivery.json`, `missions_live/se_delivery.json` |
| 7 | `missions/research_delivery.json`, `missions_live/research_delivery.json` |
| 8 | Negatives in `tests/test_preprod_supervised_mission_e2e.py` (33) |
| 9 | delivery.json fields: budget, model_*, effect_receipts |
| 10 | Fork B fix + catalog fail-closed; see INTEGRATION_EVIDENCE |
| + | Unfamiliar Goal: `missions/accept_nonce_delivery.json` + e2e oracle |

Human checkboxes remain open by design.
