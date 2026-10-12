# Cognitive organ contracts

**Status:** `CONTRACTS_LOCKED` (implementation = stub / refuse-until-wired)  
**Order:** Decomposer → Pivot/Replan → Orchestration  
**Zone:** T2 cognition — ADR-0009: no new T0/T1 Authority surfaces

Each organ contract defines **six mandatory fields**:

1. Input / Output  
2. Authority bounds  
3. Quality criteria  
4. Error handling  
5. Control-transfer rules  
6. Executable tests  

## Files

| Organ | Contract | Stub |
|-------|----------|------|
| Decomposer | `DECOMPOSER.md` | `global_os.cognition.organs.decomposer` |
| Pivot/Replan | `PIVOT_REPLAN.md` | `global_os.cognition.organs.pivot_replan` |
| Orchestration | `ORCHESTRATION.md` | `global_os.cognition.organs.orchestration` |

`LOCK.json` pins tip + parent honesty.  
Challenge still `PREREG_DRAFT` until terminal goal + stop criteria locked separately.
