# INTEGRATION_EVIDENCE

## Path

```text
Goal Contract
 → CTC Execution Brief (allowed_tools ⊆ goal caps)
 → resolve_allowed_tool_ids (catalog ∩ caps)
 → Model decision (reactive mock | live Groq)
 → validate tool_id + args
 → AuthorityKernel.decide
 → ToolGateway.execute (sole produce in handler, observation=None)
 → post_execution_artifact_verify
 → Achiever settle + Completion Gate
 → delivery.json
```

## Code surfaces

| Component | Path |
|-----------|------|
| Operator mission | `src/global_os/runtime/preprod/supervised_mission.py` |
| Tool catalog | `src/global_os/runtime/preprod/tool_catalog.py` |
| Tools | `world/tools/{repo_audit,repo_inventory,workspace_io,research_scan}.py` |
| Reactive mock | `adapters/models/observation_reactive.py` |
| Live adapter | `adapters/models/{factory,groq,openai_compat}.py` |
| CLI | `src/global_os/cli.py` (`mission start --model …`) |
| Tests | `tests/test_preprod_supervised_mission_e2e.py` (33) |
| Postconditions | `src/global_os/runtime/preprod/goal_postconditions.py` |
| Packaging | hatch force-include schemas; `validate._find_schemas_dir` |

## Integration SHAs

- Base `main` at branch cut: `5a7870b78cec39648521863ce48338709ad0a643`
- Packaging / clean-install tip: `fcc6a70`
- Branch tip evolves on `cursor/preprod-v01-rc-2907` (PR #49)

## Boundary invariants verified

- Produce only inside Gateway after Authority  
- DENY / invalid args / unknown tool → no produce  
- ALLOW → produce once; `report_hash` coherent  
- Gateway `OBSERVATION_PENDING` then post-exec verify (no pre-RECONCILED)  
- Completion Gate independent; unsupported criteria stay UNKNOWN  
