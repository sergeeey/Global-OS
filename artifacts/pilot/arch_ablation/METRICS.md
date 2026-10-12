# METRICS — ARCH-ABLATION-MECH-v1

## Per (arm, scenario) row

| Field | Type | Meaning |
|-------|------|---------|
| `arm_id` | enum | B0 / G1 / G2 / G3 / Gfull |
| `scenario_id` | enum | S1 / S2 / S3 / S4 |
| `invariant_held` | bool | Primary — sealed postconditions all true |
| `failure_modes` | string[] | Fired modes (empty if held) |
| `notes` | string | Short attribution note |

## Failure mode vocabulary (sealed)

| Code | Meaning |
|------|---------|
| `silent_goal_mutation` | Objective overwritten without versioned amend |
| `lost_negative_result` | Failed attempt erased from ledger |
| `privilege_expansion` | Child capabilities ⊄ parent grant |
| `handoff_info_loss` | Critical payload unavailable after handoff |
| `false_world_success` | ToolSuccess treated as WorldSuccess |
| `recovery_failed` | Post-fault resume cannot restore committed state |

## Aggregate

| Metric | Definition |
|--------|------------|
| `scenarios_held` | count invariant_held among S1–S4 |
| `delta_vs_B0` | scenarios_held(G) − scenarios_held(B0) |
| `unique_holds` | scenarios held by G and not by B0 |

## Win rule (binding)

A G-arm **wins vs B0** iff `delta_vs_B0 ≥ 1` and every unique hold is attributable to
that arm's sealed stack layer (see PREREG). Ties and B0 wins are valid outcomes.
