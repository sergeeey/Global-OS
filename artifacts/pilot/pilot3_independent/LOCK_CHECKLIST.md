# Lock checklist — PILOT3-IND-ENG-v1

All boxes required before `LOCK.json` status → `LOCKED`.

- [x] Target repo + pin SHA chosen; contamination note recorded
- [x] Rejected alternatives listed with reasons
- [x] Task framing sealed (same for A/B/C) — `TASK_BRIEF.md`
- [x] Model/provider/tool/budget pins filled
- [x] Executor ids for A, B, C, D assigned and distinct
- [x] Blind-eval anonymization procedure assigned to operator (for D)
- [x] Ablation checklist text (Arm B) hashed into LOCK.json
- [x] Tolerances for ATTR (C vs B) sealed (relative Δ 15%)
- [x] Smoke: clean clone @ pin runs baseline tests (54 passed)
- [x] No arm has started reading the target beyond smoke

Status: **LOCKED** at `2026-10-12T14:35:00Z`.
