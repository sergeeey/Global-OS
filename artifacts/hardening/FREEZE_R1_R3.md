# Freeze pin — post R1–R3 real-use + FC hardening

**Freeze label:** `FREEZE-R1R3-v1`  
**Freeze SHA:** `5d15600` (full `5d15600256a7afc7839f190ed3d889b33bc3217b`)  
**Date:** 2026-09-25  
**Includes:** R1–R3 real-use evidence · failure-class summary · FC-01/02/04 hardening  
**Does not include:** Windows wall preflight · literal 48h · M1.5 claim

## Freeze semantics

> Freeze = do not change the **examined machine** (`5d15600`), not “pause the project.”

- Mid-exam / mid-preflight patches on this SHA are **forbidden**.
- Defect found ⇒ record → fix on newer commit → **new freeze candidate**.
- Continuing R4/R5 on `main` is fine only if you re-freeze afterward.

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
