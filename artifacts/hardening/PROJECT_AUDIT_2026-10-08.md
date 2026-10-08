# Аудит проекта Global OS

**Дата:** 2026-10-08  
**Канон tip:** `main` @ `45446e0` (merge PR #12)  
**Аудитор:** Cloud Agent (автономный)  
**Методы:** CONSTITUTION / SPEC-ADDENDUM-V2 · RUN_STATE · capability_matrix · SCIENTIFIC_HONESTY_MAP · ACCUMULATED_CLAIM · CAMPAIGN_REPORT · ADRs · Tasktracker/Project · `run_repo_audit(deep)` · GitHub PR/CI · explore-агент по дереву кода  

**Правило честности:** `implemented approximation ≠ fulfilled contract`.

---

## 0. Вердикт (1 абзац)

Global OS — зрелый Architecture V2 runtime с сильным local/harness evidence (64 capability, 0 `PRODUCTION_PROVEN`), закрытыми научными кампаниями Y20–Y25 / T1–T3 / M-EXT1–5, и каноном на `main` в режиме **PILOT_USAGE**. Система умеет доводить внешние eng/science terminals до проверяемого исхода; **преимущество над сильным одиночным агентом и raw-capability amplification не показаны**. Следующий шаг — не новый self-exam (M-EXT6), а реальные Goal Contracts пользователя.

---

## 1. Текущий статус

| Ось | Состояние |
|-----|-----------|
| Git / CI | `main` sync; open PR = 0; последние merges #1…#12 SUCCESS |
| Sprint (`RUN_STATE`) | `PILOT_USAGE` · goal `REAL_USER_PROJECTS_PILOT_USAGE` |
| Architecture | V2 binding; ADR-0009: без новых T0/T1 поверхностей |
| Trust Kernel | **не промотирован** |
| M1.5 | `CLOSED_SCOPE_LIMITED` (LH-COGNITIVE `7ab345e`, audit `a7960d9`) |
| Capabilities | 64 · LOCAL 46 · HARNESS 18 · PRODUCTION_PROVEN **0** |
| Deep repo audit | invariants GOS-I01..I25 = 100%; forbidden hits = 0; provider boundary clean; 28 schemas |
| Tests (последний полный прогон, 2026-10-02) | 306 passed / 12 skipped на pilot-usage tip |
| Операторский dispatch | не требуется (`operator_action_required: false`) |

### Канонический claim (внешняя кампания)

> GOS способен автономно доводить реальные eng/science миссии до проверяемого terminal. Late init-Mpemba в synthetic MLP — REJECTED; early crossing — secondary SUPPORTED; Fisher — REJECTED. Преимущество GOS vs strong agent — **не показано**.

---

## 2. Что сделано (по слоям)

### 2.1 Runtime / Architecture V2 (код)

| Подсистема | Зрелость | Evidence (кратко) |
|------------|----------|-------------------|
| Goal Contract + event ledger | RUNTIME_VERIFIED_LOCAL | immutable goals, append-only |
| Authority Kernel + Tool Gateway | LOCAL + Rust harness | default-deny, effect receipts; `crates/authority_kernel` |
| Epistemic graph | LOCAL | Observation→…→Commitment + invalidation |
| Environment Compiler | LOCAL | deterministic; change gate |
| DCO / OrgCompiler | LOCAL | topologies enum; `recursive_hierarchy` fail-closed / UNPROVEN |
| Durable / Temporal / Postgres | HARNESS | kill/resume, fail-closed adapters |
| Sandbox strong (Docker) | HARNESS | network=none; CI optional skip |
| Model adapters (HTTP, no vendor SDK) | HARNESS | OpenAI-compat, Anthropic, Groq, Gemini, OpenRouter |
| Multi-provider / IV | HARNESS | GOS-I10 diversity |
| OTel / OTLP | LOCAL + live harness | fail-closed without endpoint |
| Survival suite | HARNESS | PROCESS_KILL + 13 injections |
| Repo audit tool | LOCAL | structure + deep static |

Реализация канонична в `src/global_os/`; корневые `runtime/`, `adapters/` — placeholders.

### 2.2 Empirical / trust кампании

| ID | Исход | Что доказано / не доказано |
|----|-------|----------------------------|
| Y19 | FROZEN | bundle autonomy; ≠ GOS-alone advantage |
| Y20–Y22 | TIE / NOT SHOWN | sealed science gain / reliability multiplier не подтверждены |
| R1–R3 | EARLY YES (bundle) | полезный checkable work; causal GOS NOT MEASURED |
| M1.5 | CLOSED_SCOPE_LIMITED | 48h cognitive integrity; ≠ Continual SI / production |
| T1 | REJECT | Verifier Tax 2.0 (ADR-0011) |
| T2 | KEEP | selective bounded recovery; C2 FROZEN_CANDIDATE |
| T3 | KEEP once (LIVE_LLM) | live generalization once; ≠ Trust Kernel / independent replication |
| Y24 | F1 INCONCLUSIVE / F2 REJECT | Adaptive-C NOT SHOWN |
| Y25 | REJECT | memory value NOT SHOWN at prereg strength |

### 2.3 External Real Work (M-EXT*)

| Миссия | Исход |
|--------|-------|
| M-EXT1 / EW2 urllib3#5248 | IMMUTABLE `ROOT_CAUSE_CONFIRMED` (первый «грузовой рейс») |
| M-EXT2 / EW1 | INCONCLUSIVE (degenerate labels; без retune) |
| M-EXT3 GOS vs agent | TIE; H_GSA NOT CONFIRMED (n=1) |
| M-EXT4 Mpemba triage | Agent NOT_NOVEL+ILL_POSED; post-hoc = SUCCESSFUL TRIAGE |
| M-EXT5 init-Mpemba | CAMPAIGN_CLOSED: late REJECTED (2/20), early secondary SUPPORTED (20/20), Fisher REJECTED |

PR stack #7–#12 на `main` — кампания и canon sync замержены.

### 2.4 Документы / governance

- 12 ADR (0001–0012)
- CONSTITUTION + SPEC-ADDENDUM-V2 + honesty map
- Dogfood: observe→propose→branch→test→verify→**request merge** (без autonomous T0/T1 merge архитектуры)

---

## 3. Что осталось

### 3.1 Сейчас (P0 процесса) — **Pilot usage**

```text
реальный Goal Contract пользователя
  → competing alternatives + work
  → audit / deliverable
  → лог interventions / errors / recoveries
```

- Не изобретать M-EXT6 self-exam chain  
- Не поднимать early-Mpemba secondary → primary без нового prereg  
- Не строить Immune* / ScienceKernel  
- Не промотить Trust Kernel из одного T3 KEEP  

### 3.2 Научные / product gaps (честный backlog)

| Тема | Статус | Условие продолжения |
|------|--------|---------------------|
| Raw-capability amplification | NOT SHOWN | новый prereg + сильный baseline, не rescue |
| GOS vs strong agent causal advantage | NOT SHOWN (TIE n=1) | новый протокол, не polish M-EXT3 |
| Trust Kernel / production security | NOT SHOWN | independent replication + adversarial |
| Continual SI | NOT_MEASURED | holdout после нескольких real missions |
| H-ORG recursive superiority | P1 / UNPROVEN | GOS-I30 — не axiom |
| DoD V2 fully PASS | PARTIALs remain | только с evidence |
| Per-capability `PRODUCTION_PROVEN` | 0/64 | expensive evidence only |
| Y25 follow-on / verification-budget | FUTURE | не сейчас |
| Ops quarantine (`SEPARATE_BACKLOG`) | quarantined | Docker/CRM — отдельно от GOS campaign |

### 3.3 Hygiene / honesty drift (найдено аудитом)

| Finding | Severity | Рекомендация |
|---------|----------|--------------|
| `capability_matrix` M_EXT4 `empirical: NOT_TESTED` после M-EXT5 | medium (honesty) | уточнить: empirics deferred→closed in M-EXT5 |
| `RUN_STATE.external.merge_sha` = `02acddb` (#11); tip уже `45446e0` (#12) | low | обновить merge metadata |
| `docs/IMPLEMENTATION_STATUS.md` pytest collected = **-1** (`make status` fail без pytest в PATH) | medium (tooling) | починить env / status generator |
| `autonomous_research_loop_poc` evidence: «Y20 A/B pending» | low (stale text) | обновить на scored |
| `Tasktracker` секции Active M1.5 / Deferred 48h дублируют закрытый путь `5d15600` | low (docs noise) | пометить historical / удалить unchecked leftovers |
| `ROADMAP.md` «CURRENT» ещё упоминает freeze `5d15600` как текущий | low | синхронизировать с PILOT_USAGE |
| Root placeholders `runtime/`, `adapters/` vs `src/global_os/...` | info | не путать при onboarding |

### 3.4 Явно запрещено сейчас

- Rewrite immutable M-EXT1/4/5 terminals  
- Silent fallback / LLM boolean security / direct provider вне `adapters/models/`  
- New T0/T1 architecture surfaces (ADR-0009)  
- Claim PRODUCTION_PROVEN / universal advantage без evidence  

---

## 4. Инструментальные доказательства этого аудита

| Инструмент | Результат |
|------------|-----------|
| `run_repo_audit(depth=deep)` | 1207 files; invariants 25/25; forbidden 0; provider boundary clean; 28 schemas |
| GitHub `gh pr list` | 0 open; #1–#12 merged |
| GitHub Actions `main` | last pushes SUCCESS (incl. #12) |
| Explore subagent | package map + ADR list + forbidden-pattern scan |
| `capability_matrix.json` | 64 caps; research_campaigns Y24/Y25/M_EXT* CLOSED/IMMUTABLE |
| Prior `make lint test` (2026-10-02) | ruff+mypy OK; 306 passed |
| Cursor Cloud run-info | agent on `main`, repo Global-OS |

---

## 5. Рекомендуемый следующий шаг (одна строка)

**Принять от пользователя реальный Goal Contract и вести pilot usage с аудитом и checkable deliverable** — без новой exam-цепочки.
