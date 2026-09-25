# Project.md — Global OS

**Рабочее название:** Global OS (ранее Goal OS)  
**Тип:** Durable Cognitive Runtime / Autonomous Work OS  

## Цель

Максимизировать полезную автономную работу при минимальном непроверенном доверии человека.

## Architecture V2

См. `SPEC-ADDENDUM-V2.md`.  
**DCO contracts = P0; recursive hierarchy superiority = P1 experiment (GOS-I30).**

## Текущий baseline

**Y18 failure-mode dogfood complete; pin freeze candidate next. LH validation still deferred.**

```text
LH-v1 42h scheduled survival     ✅ PASS (immutable; not literal 48h)
LH-v2.1 protocol (T+48, gate,
  OS kill, shared-state)         ✅ ready (compressed preflight PASS)
Y18 failure-mode dogfood (4)     ✅ all SUPPORTED; diversity MET
Windows 90m preflight            ⏸ deferred until freeze SHA pinned
Literal 48h / M1.5               ❌ not now
Active work                      → pin freeze candidate SHA
```

### Plan

1. **Done:** Y18 dogfood across four failure classes (evidence / effect-recovery / authority / provider degradation).  
   No open critical defects in state / recovery / authority / eval from that suite.
2. **Now:** pin freeze candidate SHA. Optional seconds-long Windows `os_process_kill` smoke only.
3. **Then:** Windows wall preflight on frozen SHA → literal 48h on a **real persistent research workload** → audit → M1.5 candidate.

Claim strength must not exceed evidence strength.

## Документы

CONSTITUTION · SPEC · **SPEC-ADDENDUM-V2** · ARCHITECTURE · AUTHORITY_MODEL · EPISTEMIC_MODEL · ORGANIZATION_MODEL · THREAT_MODEL · EVALS · ROADMAP · AGENTS · NON_GOALS
