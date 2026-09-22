# Project.md — Global OS

**Рабочее название:** Global OS (ранее Goal OS)  
**Тип:** Durable Cognitive Runtime / Autonomous Work OS  

## Цель

Максимизировать полезную автономную работу при минимальном непроверенном доверии человека.

## Architecture V2

См. `SPEC-ADDENDUM-V2.md`.  
**DCO contracts = P0; recursive hierarchy superiority = P1 experiment (GOS-I30).**

## Несущие конструкции

Goal Contract · Epistemic Kernel · Durable Runtime · Authority Kernel · Dynamic Cognitive Organization · **EnvironmentCompiler** · World Interaction · VerificationFabric · AdaptiveLearning

## Текущий baseline

**Global OS завершила Empirical Hardening и стоит у входа в Long-Horizon Validation.**

Больше не проверяем «может ли она выполнить задачу» (Y17-1..7 уже показали, что может).  
Следующий вопрос: **может ли она оставаться той же системой спустя двое суток, сбои, рестарты и изменения среды.**

```text
короткие реальные миссии        ✅
trust boundaries M1.4           ✅
live provider IV (local)        ✅
dogfood Y17-1..7                ✅
Org A/B N=7 patterns            ✅ (H-ORG not claimed)
compressed failure injections   ✅
compressed long-horizon logic   ✅
PASS criteria frozen            ✅
двойной gate 48h                ✅
настоящие 48 часов              ❌
M1.5                            ❌
Continual SI                    ❌ NOT_MEASURED
```

- **Code freeze** до результата Windows wall preflight 60–120 мин (менять код только при structural bug).
- **Next:** operator wall preflight → freeze commit/config → `GOS_REQUIRE_48H=1` + `GOS_START_RESEARCH_48H=1`.
- Оценка 48h — только по frozen PASS criteria; FAIL = ценный failure case.
- DoD V2 / PRODUCTION_PROVEN **не заявлены**
- Операторский порядок: `artifacts/hardening/long_horizon_48h/PROGRAM.md`

## Документы

CONSTITUTION · SPEC · **SPEC-ADDENDUM-V2** · ARCHITECTURE · AUTHORITY_MODEL · EPISTEMIC_MODEL · ORGANIZATION_MODEL · THREAT_MODEL · EVALS · ROADMAP · AGENTS · NON_GOALS
