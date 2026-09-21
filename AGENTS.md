# AGENTS.md — Coding Agent Policy

Перед любой работой: прочитай `CONSTITUTION.md` и `SPEC-ADDENDUM-V2.md` (Architecture V2).

## MUST

- читать `CONSTITUTION.md` первым;
- следовать Architecture V2 формуле (GoalContract + Epistemic + Durable + Authority + DCO + EnvironmentCompiler + World + Verification + AdaptiveLearning);
- закладывать **DCO contracts as P0**; не превращать H-ORG recursive superiority в axiom;
- никогда не обходить Authority Kernel;
- никогда не добавлять прямые provider calls вне `adapters/models/`;
- никогда не добавлять прямое tool execution вне Tool Gateway;
- никогда не добавлять persistent state без schema + event design;
- никогда не silently swallow errors на critical paths;
- никогда не считать README runtime proof;
- писать acceptance tests до объявления implementation complete;
- обновлять ADR при architecture changes;
- добавлять eval для cognition-related change;
- обновлять `docs/capability_matrix.json` maturity по evidence.

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
- hidden provider lock-in;
- mark PRODUCTION_PROVEN without evidence;
- invent evidence / invent missing state;
- treat model confidence as verification;
- treat recursive_hierarchy as proven optimal by default;
- self-promote adaptive changes into T0/T1.

## Development sequence (core capability)

```text
1 identify contract
2 identify invariants
3 identify authority boundary
4 identify epistemic effects
5 identify failure modes
6 write acceptance tests
7 write adversarial tests
8 implement
9 add runtime proof
10 update maturity matrix
```

Кратко:

```text
Problem → Contract → Invariant → Tests → Implementation → Runtime evidence
```

## Honesty

```text
implemented approximation ≠ fulfilled contract
```

Use capability states in `docs/capability_matrix.json`.  
Dynamic Cognitive Organization **contracts** = P0; **topology superiority** = P1 experiment.

## Trust zones

| Zone | Scope | Self-mod |
|------|-------|----------|
| T0 | Authority, core schemas, event integrity, policy bootstrap | Forbidden |
| T1 | Workflow, verification routing, epistemic kernel | Full promotion only |
| T2 | Skills, heuristics, routing, org policies | Gated by eval |
| T3 | Experiments | No privileged authority |
