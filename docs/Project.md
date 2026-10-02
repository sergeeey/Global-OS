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
                                     H_TRUST T2 KEEP + T3 KEEP once (live Groq continuation)
                                     ≠ independent replication / production / Trust Kernel
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
         T3 live-LLM replication                             KEEP (continuation; ≠ Trust Kernel)
         H_TRUST                                             T3_KEEP_LIVE — no Trust Kernel promote
         Y24 adaptive verifier complexity threshold          PREREG_LOCKED (arms not started)
Continual SI / universal advantage                           NOT MEASURED / NOT CLAIMED
Y20–Y22 scorers                                              FROZEN
Y23                                                          NOT NOW
Y25 verification-budget frontier                             FUTURE (after Y24)
```

### Plan

1. **Done:** M1.5 scope-limited closed — `artifacts/hardening/M15_DECISION.md` (EXAM `7ab345e` / AUDIT `a7960d9`).  
2. **Done:** `SAFE_AUTONOMY_BENCHMARK-v1` + H_TRUST metrics FROZEN; MCID SET_BY_VARIANCE_PILOT_v1.  
3. **Done:** T1 A/B/C under `DETERMINISTIC_FAULT_MISSIONS_v1` → **REJECT** (MIER↓ but completion tax; ADR-0011).  
4. **Done:** post-T1 diagnostics + sealed PACK-v2 + revival triggers (`T1_EVIDENCE_TABLE.md`).  
5. **Done:** T2 → **KEEP**; C2 frozen as `SELECTIVE_BOUNDED_RECOVERY-v1`; independent review CONFIRM KEEP.  
6. **Done:** T3 prereg + PACK-v3 + harness; first attempt INCONCLUSIVE (keys/quota); continuation → **KEEP** (`LIVE_LLM`, Groq).  
7. **Done / CLOSED:** live completion SHA `3ef3f44`; experiment freeze `c6523a6`; C2 unchanged; Trust Kernel not promoted.  
8. **Done:** T3 cycle closed — switch away from T3 poke.  
9. **Closed:** Y24/Y25; M-EXT1 IMMUTABLE; M-EXT2/EW1 INCONCLUSIVE; TK UNCHANGED.  
10. **Evidence:** external OSS eng result + honest science INCONCLUSIVE.  
11. **Closed:** M-EXT3 TIE on httpx#3614 — both arms hard-gated; H_GSA NOT CONFIRMED.  
12. **Audited:** M-EXT4 triage success + errata; init Mpemba UNRESOLVED / NOT TESTED.  
13. **Open:** M-EXT5 init-based Mpemba (mechanical gate first).  
14. **Not:** rewrite M-EXT4; ScienceKernel; Immune*; polish urllib3.

## Документы

CONSTITUTION · SPEC · **SPEC-ADDENDUM-V2** · **SCIENTIFIC_HONESTY_MAP** · ARCHITECTURE · AUTHORITY_MODEL · EPISTEMIC_MODEL · ORGANIZATION_MODEL · THREAT_MODEL · EVALS · ROADMAP · AGENTS · NON_GOALS · **M15_DECISION**
