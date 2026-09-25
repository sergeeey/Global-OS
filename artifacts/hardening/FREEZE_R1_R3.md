# Freeze pin — post R1–R3 real-use + FC hardening

**Freeze label:** `FREEZE-R1R3-v1`  
**Freeze SHA:** `PENDING_AFTER_COMMIT`  
**Date:** 2026-09-25  
**Includes:** R1–R3 real-use evidence · failure-class summary · FC-01/02/04 hardening  
**Does not include:** Windows wall preflight · literal 48h · M1.5 claim

## Gates at freeze

| Gate | Status |
|------|--------|
| R1–R3 terminal + independent review (R2/R3) | PASS |
| Recurring failure-class summary | PASS (`FAILURE_CLASSES_R1_R3.md`) |
| FC-01 historical rewrite guard + isolated tests | PASS |
| FC-02 SHA dir-merkle regression | PASS |
| `make lint test` | PASS |
| Compressed `make preflight-48h` | PASS (≠ wall 48h; m15_claimed=false) |
| Linux os_kill smoke | see AUDIT |
| Windows 60–120m preflight | **BLOCKED_ENVIRONMENT** (this runner is Linux) |
| Literal ≥48h real workload | **NOT STARTED** (requires freeze + Windows path) |
| M1.5 | **NOT CLAIMED** |

## Operator next (Windows)

1. `git checkout --detach <FREEZE_SHA>`
2. Follow `long_horizon_48h/WINDOWS_FROZEN_EXAM.md` with **this** SHA (not bfa58a0)
3. Only after Windows preflight PASS → literal 48h on real workload
4. Independent audit → M1.5 candidate conversation
