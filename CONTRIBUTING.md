# CONTRIBUTING.md

## Contracts-first

1. Problem  
2. Contract (JSON Schema / OpenAPI)  
3. Invariant (CONSTITUTION)  
4. Tests  
5. Implementation  
6. Runtime evidence  

## Local checks

```bash
pip install -e ".[dev]"
make check
```

## ADRs

Architecture-changing decisions go in `docs/adr/ADR-XXXX.md` with Context / Problem / Alternatives / Decision / Evidence / Trade-offs / Reversal trigger.

## Agents

Read `AGENTS.md` and `CONSTITUTION.md` before coding.
