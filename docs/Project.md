# Project.md — Global OS

**Рабочее название:** Global OS (ранее Goal OS)  
**Тип:** Durable Cognitive Runtime / Autonomous Work OS  
**Статус:** Sprint 0 + каркас Sprint 1–2  

## Цель

Максимизировать полезную автономную работу при минимальном непроверенном доверии человека.

## Architecture V2

См. `SPEC-ADDENDUM-V2.md`.  
**DCO contracts = P0; recursive hierarchy superiority = P1 experiment (GOS-I30).**

## Несущие конструкции

Goal Contract · Epistemic Kernel · Durable Runtime · Authority Kernel · Dynamic Cognitive Organization · **EnvironmentCompiler** · World Interaction · VerificationFabric · AdaptiveLearning

## Текущий baseline

- Contracts-first monorepo; EnvironmentCompiler + ChangeGate (GOS-I20)
- Epistemic graph local + EvidenceCandidate (GOS-I22)
- OrgCompiler ≥3 topologies + GoalDriftDetector; H-ORG synthetic INCONCLUSIVE
- M1 harness-verified: TemporalBridge, Postgres, OTel (+ OTLP live), Rust Authority, Docker sandbox
- Real model adapters ×2 + multi-provider verification (wire); 13 survival injections; 48h accelerated soak
- CI: schema + ruff + mypy + pytest (+ cargo / Temporal / Postgres / Docker / OTLP)
- DoD V2 / PRODUCTION_PROVEN не заявлены; next = live keys at scale + wall 48h + H-ORG scientific acceptance (P1)

## Документы

CONSTITUTION · SPEC · **SPEC-ADDENDUM-V2** · ARCHITECTURE · AUTHORITY_MODEL · EPISTEMIC_MODEL · ORGANIZATION_MODEL · THREAT_MODEL · EVALS · ROADMAP · AGENTS · NON_GOALS

