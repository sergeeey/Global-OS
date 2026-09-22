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
- OrgCompiler ≥3 topologies + GoalDriftDetector; H-ORG-1..4 split; claims not accepted
- M1 Reality Contact nearly closed (Docker/OTLP/models/survival/soak wire)
- **ADR-0009:** architecture freeze → Empirical Science until M1.5
- Goal Integrity Score + eval contracts; incidents + DoD V2 gate + dogfood (no auto-merge)
- Free pins: OpenRouter Nemotron 550b / Groq gpt-oss-120b / Gemini 3.6-flash; `run_hrsn_measured` + scheduled 48h soak
- **Operator Reality Contact:** 3-provider smoke + live H-ENV/H-RSN JSON (claim=false; winner often A — ladder B–E still prompt-conditioned)
- **Active mode:** dogfood — `Y17 mission → GlobalOS → failure → fix → replay` (M1.5 = IN PROGRESS; 48h paused)
- **Y17-1..Y17-5** done across Fisher / model-selection / causal / RMT / **forecasting-holdout**
- **Provider IV:** cloud BLOCKED; local ≥2 free keys still required for `unblocked: true`
- **Active mode:** M1.4 Trust Boundary Hardening (ADR-0010) before further dogfood/48h
- **Y17-1..Y17-5** done across Fisher / model-selection / causal / RMT / forecasting-holdout
- **Provider IV:** cloud BLOCKED; local ≥2 free keys still required for `unblocked: true`
- **Org A/B** N=5: PATTERNS_OBSERVABLE_H_ORG_NOT_CLAIMED (H-ORG not claimed)
- **M1.4 in progress:** proposal-bound ExecutionToken, approval hard-bind, immutable epistemic,
  cold-restart restore, effect reconciliation; CI paths/lockfile/Temporal pin
- **Next:** CI green → local IV → Y17-6/7 + Org N↑ → 48h persistent research → only then M1.5
- DoD V2 / M1.4 closed / M1.5 closed / PRODUCTION_PROVEN **не заявлены**


## Документы

CONSTITUTION · SPEC · **SPEC-ADDENDUM-V2** · ARCHITECTURE · AUTHORITY_MODEL · EPISTEMIC_MODEL · ORGANIZATION_MODEL · THREAT_MODEL · EVALS · ROADMAP · AGENTS · NON_GOALS

