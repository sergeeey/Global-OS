# Lock checklist — PILOT3-IND-ENG-v1

All boxes required before `LOCK.json` status → `LOCKED`.

- [ ] Target repo + pin SHA chosen; contamination note recorded
- [ ] Rejected alternatives listed with reasons
- [ ] Task framing sealed (same for A/B/C)
- [ ] Model/provider/tool/budget pins filled
- [ ] Executor ids for A, B, C, D assigned and distinct
- [ ] Blind-eval anonymization procedure assigned to operator (for D)
- [ ] Ablation checklist text (Arm B) hashed into LOCK.json
- [ ] Tolerances for ATTR (C vs B) sealed
- [ ] Smoke: clean clone @ pin runs baseline tests
- [ ] No arm has started reading the target beyond smoke

Until then: `PREREG_DRAFT` only.
