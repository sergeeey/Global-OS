# Project.md — Global OS

**Рабочее название:** Global OS (ранее Goal OS)  
**Тип:** Durable Cognitive Runtime / Autonomous Work OS  

## Цель

Максимизировать полезную автономную работу при минимальном непроверенном доверии человека.

## Architecture V2

См. `SPEC-ADDENDUM-V2.md`.  
**DCO contracts = P0; recursive hierarchy superiority = P1 experiment (GOS-I30).**

## Текущий baseline

**Long-Horizon protocol repaired; validation deferred while real-world hardening continues.**

```text
LH-v1 42h scheduled survival     ✅ PASS (immutable; not literal 48h)
LH-v2.1 protocol (T+48, gate,
  OS kill, shared-state)         ✅ ready (compressed preflight PASS)
Windows 90m preflight            ⏸ deferred until freeze
Literal 48h / M1.5               ❌ not now
Active work                      → real dogfood missions + fixes
```

### Plan

1. **Now:** real dogfood (2–4 distinct mission classes) → failure cases → minimal fix → regression.  
   Optional seconds-long Windows `os_process_kill` smoke only.  
   No 90m preflight / no 48h while code is still moving.
2. **Freeze when:** no open critical defects in state / recovery / authority / eval protocol.
3. **Then:** freeze SHA → Windows wall preflight → literal 48h on a **real persistent research workload** (not synthetic-only) → audit → M1.5 candidate.

Claim strength must not exceed evidence strength.

## Документы

CONSTITUTION · SPEC · **SPEC-ADDENDUM-V2** · ARCHITECTURE · AUTHORITY_MODEL · EPISTEMIC_MODEL · ORGANIZATION_MODEL · THREAT_MODEL · EVALS · ROADMAP · AGENTS · NON_GOALS
