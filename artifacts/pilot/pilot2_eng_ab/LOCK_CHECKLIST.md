# Lock checklist — PILOT2-ENG-AB-v1

Mark each box before arm execution. Incomplete → do not start.

- [x] Target repo + pin SHA recorded in `LOCK.json` (`mcp-bouncer@45af092`)
- [x] Identical snapshot recipe recorded (tree OID in `LOCK.json`)
- [x] Model/provider/tools/budgets pinned in `LOCK.json` (SAME_EXECUTOR_DUAL_PROTOCOL)
- [x] Finding rubric sealed (`FINDING_RUBRIC.md`)
- [x] Metrics sealed (`METRICS.md`; α default noted)
- [x] Ordered eval thresholds acknowledged
- [x] Baseline (A) is strong (not crippled) — direct eng protocol
- [x] Network/secrets policy identical — offline after clone
- [x] Human intervention script — none used (0 interventions)
- [x] Independent checker — sealed repro pytest pack
- [x] PhaseBreak hygiene completed (PR #1 `0161463`)
- [x] No Global-OS / PhaseBreak as target

**Target lock (Global-OS tip):** `4507051`  
**Target lock time (UTC):** `2026-10-12T11:21:00Z`  
**Arm-start / decision tip:** `9fa1fd6`  
**Operator:** cloud-agent (autonomous Pilot 2 exec)
