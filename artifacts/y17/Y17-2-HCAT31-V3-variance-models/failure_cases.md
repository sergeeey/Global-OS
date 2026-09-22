# failure_cases.md — Y17-2 classification

| id | class | recurring? | fix? |
|---|---|---|---|
| Y17-2-FC-IV | ENVIRONMENT_GAP | yes (Y17-1) | already handled: BLOCKED_ENVIRONMENT + continue |
| Y17-2-FC-PRIOR-CLOSED | RESEARCH_METHOD_GAP (caught) | yes (Y17-FC-003) | PriorWorkReframe applied; no new subsystem |
| nested_F REJECTED | NOT_A_BUG | n/a | scientific null preserved (GOS-I11) |
| empty secondary contradiction | NOT_A_BUG | n/a | primes agreed directionally with REJECTED |

## Phase-4 product fix applied

`run_research_mission` now promotes `contradictory_evidence` from experiment raw
metrics to top-level `contradictory_evidence.json` (regression-tested).
