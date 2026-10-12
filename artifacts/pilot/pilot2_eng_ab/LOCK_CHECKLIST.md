# Lock checklist — PILOT2-ENG-AB-v1

Mark each box before arm execution. Incomplete → do not start.

- [x] Target repo + pin SHA recorded in `LOCK.json` (`mcp-bouncer@45af092`)
- [x] Identical snapshot recipe recorded (tree OID in `LOCK.json`)
- [ ] Model/provider/tools/budgets pinned in `PREREG.md` / `LOCK.json`
- [x] Finding rubric sealed (`FINDING_RUBRIC.md`)
- [x] Metrics sealed (`METRICS.md`; α default noted)
- [x] Ordered eval thresholds acknowledged
- [ ] Baseline (A) is strong (not crippled) — confirm at arm start
- [ ] Network/secrets policy identical — confirm at arm start
- [ ] Human intervention script prepared
- [ ] Independent checker assigned
- [x] PhaseBreak hygiene completed (PR #1 `0161463`)
- [x] No Global-OS / PhaseBreak as target

**Target lock (Global-OS tip):** `4507051`  
**Target lock time (UTC):** `2026-10-12T11:21:00Z`  
**Arm-start lock (provider pins):** _______________  
**Operator:** _______________
