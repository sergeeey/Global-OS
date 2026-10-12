# Pilot 3 Pack — notes

- **Role:** Pilot 3 Pack (strong single agent), Protocol A (normal engineering audit).  
- **Scope:** `/tmp/pilot/p3-arm-A` @ `47c232b`, `tools/workflow-controller/` only.  
- **Forbidden respected:** no `out_P/C/D`, no PROTOCOL_B/C/D, no Pilot 2 packs, no network after deps.  
- **Start (UTC):** 2026-10-12T14:32:49Z  
- **Approach:** Map modules (artifact/security gates, tool policy, MCP, issue flow/runner/state, event log) → adversarial probes on policy paths, event-log consistency, scanner exit codes, sync/plan coupling → confirm with scripts → minimal patches + fail-then-pass regressions → write `out_P` only.  
- **Smoke:** existing suite green (54); not counted as findings. Post-fix in-tree suite 55 (added one policy unit test).  
- **Not pursued:** style nits, architecture rewrite, XXE/DoS on coverage XML, weak README substring matching (hygiene only).  
- **Fix location:** patches live in the Pack checkout for verification; deliverable patch copy in `REPRO/proposed_fixes.patch`. Upstream merge is out of band for this arm.
