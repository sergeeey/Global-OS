# Project.md — Global OS

**Рабочее название:** Global OS (ранее Goal OS)  
**Тип:** Durable Cognitive Runtime / Autonomous Work OS  

## Цель

Максимизировать полезную автономную работу при минимальном непроверенном доверии человека.

## Architecture V2

См. `SPEC-ADDENDUM-V2.md`.  
**DCO contracts = P0; recursive hierarchy superiority = P1 experiment (GOS-I30).**

## Текущий baseline

**Freeze candidate pinned (`bfa58a0`). Next: Windows preflight → literal 48h exam of this SHA.**

```text
LH-v1 42h scheduled survival     ✅ PASS (immutable; not literal 48h)
LH-v2.1 protocol (T+48, gate,
  OS kill, shared-state)         ✅ ready (compressed preflight PASS)
Y18 failure-mode dogfood (4)     ✅ all SUPPORTED; diversity MET
Freeze candidate                 ✅ bfa58a0
Windows 90m preflight            → next on frozen SHA
Literal 48h / M1.5               ❌ after preflight only
```

### Plan

1. **Done:** Y18 dogfood (four failure classes) + freeze candidate pin `bfa58a0`.
2. **Now:** optional seconds-long Windows `os_process_kill` smoke; then Windows wall preflight on `bfa58a0`.  
   (Linux os_kill smoke already PASS — not a Windows substitute.)
3. **Then:** literal 48h on a **real persistent research workload** as final exam of this frozen SHA → audit → M1.5 candidate.

Claim strength must not exceed evidence strength.

## Документы

CONSTITUTION · SPEC · **SPEC-ADDENDUM-V2** · ARCHITECTURE · AUTHORITY_MODEL · EPISTEMIC_MODEL · ORGANIZATION_MODEL · THREAT_MODEL · EVALS · ROADMAP · AGENTS · NON_GOALS
