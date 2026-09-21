# AGENTS.md — Coding Agent Policy

Перед любой работой: прочитай `CONSTITUTION.md`.

## MUST

- читать `CONSTITUTION.md` первым;
- никогда не обходить Authority Kernel;
- никогда не добавлять прямые provider calls вне `adapters/models/`;
- никогда не добавлять прямое tool execution вне Tool Gateway;
- никогда не добавлять persistent state без schema + event design;
- никогда не silently swallow errors на critical paths;
- никогда не считать README runtime proof;
- писать acceptance tests до объявления implementation complete;
- обновлять ADR при architecture changes;
- добавлять eval для cognition-related change.

## MUST NOT (forbidden patterns)

- LLM boolean security decisions;
- `agent.execute_anything()` / `Bash(*)`;
- regex parsing nested JSON как contract validation;
- silent fallback to allow;
- silent network fallback;
- mutable goal object (in-place overwrite);
- vector DB as truth store;
- LLM-generated evidence marker как verification;
- direct worker-to-secret access;
- direct model-to-world effect;
- same-agent self-certification;
- unbounded retries / unbounded agent spawning;
- hidden provider lock-in.

## Development sequence

```text
Problem → Contract → Invariant → Tests → Implementation → Runtime evidence
```

## Trust zones

| Zone | Scope | Self-mod |
|------|-------|----------|
| T0 | Authority, core schemas, event integrity, policy bootstrap | Forbidden |
| T1 | Workflow, verification routing, epistemic kernel | Full promotion only |
| T2 | Skills, heuristics, routing, org policies | Gated by eval |
| T3 | Experiments | No privileged authority |
