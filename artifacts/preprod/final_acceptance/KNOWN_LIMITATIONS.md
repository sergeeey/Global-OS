# KNOWN_LIMITATIONS

1. **Profile:** PREPROD_SUPERVISED only — one operator, one active mission.  
2. **Live model quality:** may propose invalid args or non-preferred tools; loop recovers but may burn cycles.  
3. **Write oracle:** Completion binds on tool receipt/verify; filename `FIX_APPLIED.txt` is not a separate filesystem oracle in Completion Gate.  
4. **Tool set:** catalog is small (audit/inventory/read/write/research.scan) — not a general ToolKernel.  
5. **No Challenge-GA**, no Continual SI claim, no PRODUCTION_PROVEN.  
6. **No multi-hour soak**; kill/recovery is a short real-process probe.  
7. **HMAC / action-binding residual** not claimed solved.  
8. **Clean-env install** documented but not re-validated by a second human machine in this run.  
9. **Paid LLM providers** not authorized/used.  
10. **ADR-0009:** no new T0/T1 kernels added.  
