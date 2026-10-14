# RELEASE_GATE_EVIDENCE

Maps `PREPROD_RELEASE_GATE.md` / `RELEASE_GATE.md` criteria to proof.

| # | Evidence pointer |
|---|------------------|
| 1 | `OPERATOR.md` + `CLEAN_INSTALL.md` / `CLEAN_INSTALL_MISSION.json` (wheel accept-nonce) |
| 2 | CLI `gos mission start`; e2e `test_supervised_mission_end_to_end_delivery` |
| 3 | e2e pause/cancel; budget insufficient negative |
| 4 | `scripts/preprod_real_kill_recovery.py` + `recovery/REAL_KILL_RECOVERY.json` |
| 5 | Same + `preprod_crash_window_recovery.py` + `CRASH_WINDOW_RECOVERY.json` |
| 6 | `missions/se_delivery.json`; live re-run SE PARTIAL (`LIVE_RERUN_RESULTS.md`) |
| 7 | `missions/research_delivery.json`; live research SUCCEEDED |
| 8 | Negatives in e2e + packaged-asset tests |
| 9 | delivery.json fields: budget, model_*, effect_receipts |
| 10 | Fork B fix + catalog fail-closed; see INTEGRATION_EVIDENCE |
| + | Unfamiliar Goal: `missions/accept_nonce_delivery.json` + e2e oracle |

Human checkboxes remain open by design.
