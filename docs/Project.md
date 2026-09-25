# Project.md — Global OS

**Рабочее название:** Global OS (ранее Goal OS)  
**Тип:** Durable Cognitive Runtime / Autonomous Work OS  

## Цель

Максимизировать полезную автономную работу при минимальном непроверенном доверии человека.

## Architecture V2

См. `SPEC-ADDENDUM-V2.md`.  
**DCO contracts = P0; recursive hierarchy superiority = P1 experiment (GOS-I30).**

## Текущий baseline

**Frozen validation of `bfa58a0`. Next: Windows os_kill smoke → Windows wall preflight. Literal 48h only after PASS.**

```text
Y18 failure-mode dogfood (4)     ✅ SUPPORTED; diversity MET
Freeze candidate                 ✅ bfa58a0 (under exam — do not mutate)
Linux OS kill smoke              ✅ PASS
Windows OS kill smoke            → REQUIRED next
Windows 60–120m wall preflight   → after Windows smoke PASS
Literal 48h / M1.5               ❌ gated on Windows preflight PASS
```

### Plan

1. **Done:** Y18 + freeze pin `bfa58a0` + Linux os_kill smoke.
2. **Now (operator Windows):** checkout **exactly** `bfa58a0` (no `git pull`) → Windows os_kill smoke → Windows wall preflight 60–120m.  
   Runbook: `artifacts/hardening/long_horizon_48h/WINDOWS_FROZEN_EXAM.md`.  
   Windows FAIL ⇒ new SHA / new freeze (do not patch this freeze).
3. **Then:** literal 48h as integration exam of `bfa58a0` → audit → M1.5 candidate.  
   Keep `Y18-4-FC-IV` as `BLOCKED_ENVIRONMENT`.

Claim strength must not exceed evidence strength.

## Документы

CONSTITUTION · SPEC · **SPEC-ADDENDUM-V2** · ARCHITECTURE · AUTHORITY_MODEL · EPISTEMIC_MODEL · ORGANIZATION_MODEL · THREAT_MODEL · EVALS · ROADMAP · AGENTS · NON_GOALS
