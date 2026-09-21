# Project.md — Global OS

**Рабочее название:** Global OS (ранее Goal OS)  
**Тип:** Durable Cognitive Runtime / Autonomous Work OS  
**Статус:** Sprint 0 + каркас Sprint 1–2  

## Цель

Максимизировать полезную автономную работу при минимальном непроверенном доверии человека.

## Несущие конструкции

Goal Contract · Epistemic Kernel · Durable Runtime · Authority Kernel · Dynamic Cognitive Organization · World Interaction · Verification · Adaptation

## Текущий baseline

- Contracts-first monorepo
- JSON Schema для core entities
- Python: GoalStore, EventLedger, AuthorityKernel, ToolGateway, EpistemicStore
- CI: schema validation + ruff + mypy + pytest
- Rust Authority Service — следующий hardening шаг (сейчас typed Python stub с теми же инвариантами)

## Документы

CONSTITUTION · SPEC · ARCHITECTURE · AUTHORITY_MODEL · EPISTEMIC_MODEL · ORGANIZATION_MODEL · THREAT_MODEL · EVALS · ROADMAP · AGENTS · NON_GOALS
