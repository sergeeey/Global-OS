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
         C2 contract SELECTIVE_BOUNDED_RECOVERY-v1           FROZEN_CANDIDATE
         T3 live-LLM replication                             INCONCLUSIVE (keys OK; Groq TPD exhausted)
         H_TRUST                                             CONTINUE_MA_LINE (await quota / alt free keys)
Continual SI / universal advantage                           NOT MEASURED / NOT CLAIMED
Y20–Y22 scorers                                              FROZEN
Y23                                                          NOT NOW
```

### Plan

1. **Done:** M1.5 scope-limited closed — `artifacts/hardening/M15_DECISION.md` (EXAM `7ab345e` / AUDIT `a7960d9`).  
2. **Done:** `SAFE_AUTONOMY_BENCHMARK-v1` + H_TRUST metrics FROZEN; MCID SET_BY_VARIANCE_PILOT_v1.  
3. **Done:** T1 A/B/C under `DETERMINISTIC_FAULT_MISSIONS_v1` → **REJECT** (MIER↓ but completion tax; ADR-0011).  
4. **Done:** post-T1 diagnostics + sealed PACK-v2 + revival triggers (`T1_EVIDENCE_TABLE.md`).  
5. **Done:** T2 → **KEEP**; C2 frozen as `SELECTIVE_BOUNDED_RECOVERY-v1`; independent review CONFIRM KEEP.  
6. **Done:** T3 prereg + PACK-v3 + harness → **INCONCLUSIVE** (live keys unavailable; SHA `c6523a6`).  
7. **Next:** load free live keys → re-run T3 as **continuation** (same prereg/pack; no C2 edit; no PACK-v4) → KEEP/REJECT/INCONCLUSIVE.  
   Runner now fail-closed on post-unseal drift and always embeds continuation binding + `LIVE_PROVENANCE.json`.  
8. **Separate ops:** `artifacts/ops/SEPARATE_BACKLOG.md`.  
9. **Not now:** Trust Kernel promote; reopen M1.5; rewrite T1 MCID; Y23; retune C2; invent PACK-v4 to reset.

## Документы

CONSTITUTION · SPEC · **SPEC-ADDENDUM-V2** · **SCIENTIFIC_HONESTY_MAP** · ARCHITECTURE · AUTHORITY_MODEL · EPISTEMIC_MODEL · ORGANIZATION_MODEL · THREAT_MODEL · EVALS · ROADMAP · AGENTS · NON_GOALS · **M15_DECISION**
