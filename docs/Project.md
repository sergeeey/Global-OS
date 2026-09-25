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

**Empirical Hardening CLOSED. Wall-clock long-horizon program PASS. M1.5 = candidate for closure review (not auto-claimed).**

```text
короткие реальные миссии        ✅
trust boundaries M1.4           ✅
live provider IV (local)        ✅
dogfood Y17-1..7                ✅
Org A/B N=7 patterns            ✅ (H-ORG not claimed)
compressed LH + portability fix ✅
PASS criteria frozen            ✅
wall_48h WALL_CLOCK_48H         ✅ PASS (operator Windows)
M1.5                            ⏳ CANDIDATE (review)
Continual SI                    ❌ NOT_MEASURED
H-ORG                           ❌ not claimed
PRODUCTION_PROVEN               ❌ not claimed
```

- Wall evidence: `artifacts/hardening/long_horizon_48h/wall_48h/` (`passed=true`, GIS PASS, 9/9 injections, 11/11 criteria; elapsed ≈42.0h through T+42 schedule).
- Next: audit artifacts + confirm no hidden intervention → decide M1.5 closure.
- H-ORG and Continual SI remain **separate** post-M1.5 research questions.

## Документы

CONSTITUTION · SPEC · **SPEC-ADDENDUM-V2** · ARCHITECTURE · AUTHORITY_MODEL · EPISTEMIC_MODEL · ORGANIZATION_MODEL · THREAT_MODEL · EVALS · ROADMAP · AGENTS · NON_GOALS
