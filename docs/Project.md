# Project.md — Global OS

**Рабочее название:** Global OS (ранее Goal OS)  
**Тип:** Durable Cognitive Runtime / Autonomous Work OS  

## Цель

Максимизировать полезную автономную работу при минимальном непроверенном доверии человека.

## Architecture V2

См. `SPEC-ADDENDUM-V2.md`.  
**DCO contracts = P0; recursive hierarchy superiority = P1 experiment (GOS-I30).**

## Текущий baseline

**Scientific dogfood (Y19) active. LH 96m/48h deferred. `bfa58a0` = intermediate stable point.**

```text
Y18 failure-mode diversity       ✅ MET
bfa58a0                          ✅ intermediate stable
Linux OS kill smoke              ✅ PASS
Windows OS kill smoke            ✅ PASS on bfa58a0 (PIDs distinct)
Windows 96m / literal 48h        ⏸ deferred
Y19-H1                           ✅ REJECTED (spectral < MCID)
Y19-H2                           ✅ SUPPORTED (size/entropy > activity-only)
Y19-H3                           ✅ SUPPORTED (H2 robust under stress)
Y19-H4                           ✅ REJECTED (entropy dies under N control → mostly size)
M1.5                             ❌ not claimed
```

### Plan

1. **Done:** Windows `os_kill` smoke on exact `bfa58a0` PASS. Y19-H1/H2 science running.  
2. **Now:** continue Y19 scientific dogfood (unknown-answer; honest REJECTED valued).  
3. **Not now:** 96m preflight, literal 48h, M1.5 claim.  
4. **Later:** after science dogfood stabilizes → new freeze SHA → Windows preflight → 48h exam.

Claim strength must not exceed evidence strength. Honest `REJECTED` on Y19 is valuable.

## Документы

CONSTITUTION · SPEC · **SPEC-ADDENDUM-V2** · ARCHITECTURE · AUTHORITY_MODEL · EPISTEMIC_MODEL · ORGANIZATION_MODEL · THREAT_MODEL · EVALS · ROADMAP · AGENTS · NON_GOALS
