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
- M1 harness-verified: TemporalBridge, Postgres durable, OTel (+ OTLP fail-closed), Rust Authority
- CI: schema validation + ruff + mypy + pytest (+ cargo / Temporal / Postgres where configured)
- DoD v0.1 ещё не PRODUCTION_PROVEN; next: live OTLP collector, real-model evals, M2 organization depth

## Документы

CONSTITUTION · SPEC · ARCHITECTURE · AUTHORITY_MODEL · EPISTEMIC_MODEL · ORGANIZATION_MODEL · THREAT_MODEL · EVALS · ROADMAP · AGENTS · NON_GOALS
