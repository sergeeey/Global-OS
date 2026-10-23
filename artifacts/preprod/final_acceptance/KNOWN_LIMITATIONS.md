# KNOWN_LIMITATIONS

1. **Profile:** PREPROD_SUPERVISED only — one operator, one active mission.  
2. **Live model quality:** may propose invalid args or non-preferred tools; live SE re-run stayed **PARTIAL** (no FIX_APPLIED) while research SUCCEEDED — see `LIVE_RERUN_RESULTS.md`.  
3. **Write postcondition:** goal-specific path+disk bind (`goal_postconditions.py`) prevents wrong filenames from satisfying FIX_APPLIED / ACCEPT_* criteria; Completion Gate still depends on Gateway receipts + that bind — not a separate external auditor process.  
4. **Tool set:** catalog is small (audit/inventory/read/write/research.scan) — not a general ToolKernel.  
5. **No Challenge-GA**, no Continual SI claim, no PRODUCTION_PROVEN.  
6. **No multi-hour soak**; kill/recovery is a short real-process probe.  
7. **HMAC / action-binding residual** not claimed solved.  
8. **Clean-env install:** agent-proven wheel mission (`CLEAN_INSTALL_MISSION.json`); second-human machine confirmation still open.  
9. **Paid LLM providers** not authorized/used.  
10. **ADR-0009:** no new T0/T1 kernels added.  
