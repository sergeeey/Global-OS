# Project.md — Global OS

**Рабочее название:** Global OS (ранее Goal OS)  
**Тип:** Durable Cognitive Runtime / Autonomous Work OS  
**Статус:** Sprint 0 + каркас Sprint 1–2  

## Цель

Максимизировать полезную автономную работу при минимальном непроверенном доверии человека.

## Несущие конструкции

Goal Contract · Epistemic Kernel · Durable Runtime · Authority Kernel · Dynamic Cognitive Organization · **EnvironmentCompiler** · World Interaction · VerificationFabric · AdaptiveLearning

## Текущий baseline

- Contracts-first monorepo; EnvironmentCompiler + ChangeGate (GOS-I20)
- Epistemic graph local: Observation→Belief→Claim→Model→Forecast→Decision→Commitment
- MissionAssigner (outcome contracts) + EventReplay status projections
- CI: schema validation + ruff + mypy + pytest
- M1 ещё CONTRACTED: Temporal, Postgres durable shared state, distributed OTel
- Rust Authority Service — следующий hardening шаг после contract freeze

## Документы

CONSTITUTION · SPEC · ARCHITECTURE · AUTHORITY_MODEL · EPISTEMIC_MODEL · ORGANIZATION_MODEL · THREAT_MODEL · EVALS · ROADMAP · AGENTS · NON_GOALS
