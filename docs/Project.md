# Project.md — Global OS

**Рабочее название:** Global OS (ранее Goal OS)  
**Тип:** Durable Cognitive Runtime / Autonomous Work OS  

## Цель

Максимизировать полезную автономную работу при минимальном непроверенном доверии человека.

## Architecture V2

См. `SPEC-ADDENDUM-V2.md`.  
**DCO contracts = P0; recursive hierarchy superiority = P1 experiment (GOS-I30).**

## Thesis (working stance — see `docs/SCIENTIFIC_HONESTY_MAP.md`)

**Не говорим:** «GOS не усиливает интеллект.»  
**Говорим:** на протестированных классах задач **не показано** измеримое улучшение primary outcome vs сильный baseline (`NULL ≠ zero effect`).

```text
Raw-capability amplification:        NOT SHOWN
Trust / long-horizon amplification:  PARTIAL — M1.5 scope-limited CLOSED (cognitive 48h integrity)
                                     H_TRUST T2 KEEP on PACK-v2 (selective recovery; eval harness)
                                     ≠ production / live-LLM / Trust Kernel
```

## Evidence map

```text
Y20–Y22  raw primary-outcome advantage vs strong baseline?  NOT SHOWN
R1–R3    useful autonomous checkable real work (bundle)?     EARLY YES
         causal GOS advantage?                               NOT MEASURED
M1.5     LH-COGNITIVE 48h integrity @7ab345e                 CLOSED_SCOPE_LIMITED
         (audit PASS; ≠ production / Continual SI / causal advantage)
Post     SAFE_AUTONOMY_BENCHMARK-v1 metrics                   FROZEN
         Mission Assurance T1 A/B/C                          REJECT (Verifier Tax 2.0)
         T2 selective recovery on PACK-v2                    KEEP (FSR=1.0, URR=0, MIER=0)
         H_TRUST                                             CONTINUE_MA_LINE (eval harness)
Continual SI / universal advantage                           NOT MEASURED / NOT CLAIMED
Y20–Y22 scorers                                              FROZEN
Y23                                                          NOT NOW
```

### Plan

1. **Done:** M1.5 scope-limited closed — `artifacts/hardening/M15_DECISION.md` (EXAM `7ab345e` / AUDIT `a7960d9`).  
2. **Done:** `SAFE_AUTONOMY_BENCHMARK-v1` + H_TRUST metrics FROZEN; MCID SET_BY_VARIANCE_PILOT_v1.  
3. **Done:** T1 A/B/C under `DETERMINISTIC_FAULT_MISSIONS_v1` → **REJECT** (MIER↓ but completion tax; ADR-0011).  
4. **Done:** post-T1 diagnostics + sealed PACK-v2 + revival triggers (`T1_EVIDENCE_TABLE.md`).  
5. **Done:** T2 prereg + selective recovery + PACK-v2 unseal → **KEEP** (`T2/T2_DECISION.md`, ADR-0012).  
6. **Next:** continue Mission Assurance line under honesty bounds **or** advance M2/Y19; no Trust Kernel promote.  
7. **Separate ops:** `artifacts/ops/SEPARATE_BACKLOG.md`.  
8. **Not now:** reopen M1.5/48h; rewrite T1 MCID; Y23; Trust Kernel / T0–T1 promote from T2 KEEP.

## Документы

CONSTITUTION · SPEC · **SPEC-ADDENDUM-V2** · **SCIENTIFIC_HONESTY_MAP** · ARCHITECTURE · AUTHORITY_MODEL · EPISTEMIC_MODEL · ORGANIZATION_MODEL · THREAT_MODEL · EVALS · ROADMAP · AGENTS · NON_GOALS · **M15_DECISION**
