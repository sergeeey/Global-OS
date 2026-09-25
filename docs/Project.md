# Project.md — Global OS

**Рабочее название:** Global OS (ранее Goal OS)  
**Тип:** Durable Cognitive Runtime / Autonomous Work OS  

## Цель

Максимизировать полезную автономную работу при минимальном непроверенном доверии человека.

## Architecture V2

См. `SPEC-ADDENDUM-V2.md`.  
**DCO contracts = P0; recursive hierarchy superiority = P1 experiment (GOS-I30).**

## Текущий baseline

**Y20 prereg frozen at `278c10d`. Ready to run Arm A only. Architecture freeze.**

```text
Y19                         CLOSED / evidence packed
Y19 autonomy attribution    bundle-level only
Y20 prereg                  LOCKED @ 278c10d
Arm A                       NOT RUN
Arm B                       NOT RUN
sealed ground truth         UNSEEN
blind scorer                LOCKED
equal caps                  LOCKED
Global OS advantage         NOT PROVEN
cross-domain transfer       NOT PROVEN
continual SI                NOT MEASURED
M1.5                        NOT CLAIMED
```

### Plan

1. **Now:** execute Arm A (strong baseline) → freeze `arms/A` → then Arm B → then unseal/score.  
2. **Forbidden until COMPARISON_REPORT:** architecture “improvements”, unseal early, cripple A, change scorer.  
3. **Later:** Y21/Y22 → freeze SHA → LH. Not now.

Claim strength must not exceed evidence strength. Need **truth about the system**, not a forced GOS win.

## Документы

CONSTITUTION · SPEC · **SPEC-ADDENDUM-V2** · ARCHITECTURE · AUTHORITY_MODEL · EPISTEMIC_MODEL · ORGANIZATION_MODEL · THREAT_MODEL · EVALS · ROADMAP · AGENTS · NON_GOALS
