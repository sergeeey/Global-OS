# Отчёт: внешняя экзаменационная кампания Global OS

**Дата:** 2026-10-02  
**Ветка:** `cursor/m-ext4-mpemba-mission-2907` @ `8d2b5b2`  
**Sprint:** `M_EXT5_INIT_MPEMBA_OPEN`  
**Архитектура Global OS:** без изменений ради optics (ADR-0009 соблюдён)

---

## 1. Зачем была кампания

После закрытия внутренних кампаний (Y24/Y25 REJECT, T3 KEEP без Trust Kernel) цель сместилась:

```text
не «доказать, что Global OS умен»
а «получить проверяемый внешний результат / честный научный terminal»
```

Контракт: `artifacts/external/CONTRACT/EXTERNAL_REAL_WORK.md`.

---

## 2. Сводная таблица исходов

| Миссия | Класс | Исход | Что это значит |
|--------|-------|-------|----------------|
| **M-EXT1 / EW2** | OSS eng | `ROOT_CAUSE_CONFIRMED` IMMUTABLE | Реальный urllib3#5248: repro → H1 → patch → regression fail/pass |
| **M-EXT2 / EW1** | Science | `INCONCLUSIVE` | Sealed science; degenerate labels; без retune |
| **M-EXT3 / GSA** | Comparison | `TIE` | GOS vs strong agent на httpx#3614; оба HG=1; H_GSA NOT CONFIRMED |
| **M-EXT4 / EW4** | Science triage | Agent: `NOT_NOVEL`+`ILL_POSED`; Audit: **SUCCESSFUL TRIAGE** | Автономный scientific triage; эмпирика не закрыта |
| **M-EXT5 / EW5** | Science (residual) | H_EFFECT **REJECTED**; early sec. SUPPORTED; H_FISHER **REJECTED** | Late init-Mpemba нет; early threshold-dependent crossing есть; не Fisher |

**Trust Kernel:** не промотирован.  
**Immune* / ScienceKernel:** не строились.

---

## 3. Что сделано по миссиям

### 3.1 M-EXT1 — первый «грузовой рейс»

- Задача: urllib3#5248 (`blocksize=0` → silent empty body).
- Цикл: reproduce → competing explanations → counterevidence → root cause → patch → regression.
- Root cause: `read(0)` → `b""` трактуется как EOF.
- Hard gate выполнен; GOS-код не меняли.
- Статус: **IMMUTABLE** — не полировать ради self-score.

### 3.2 M-EXT2 — честная наука с holdout

- Coupled logistic early predictor vs baseline.
- Locked label → 0 negatives → class-balance gate → **INCONCLUSIVE**.
- Урок Y24 применён: без post-hoc retune.

### 3.3 M-EXT3 — предмет для сравнения появился

- Pin: encode/httpx#3614 (`base_url` query corruption).
- Arm A (strong agent) и Arm B (GOS): оба `ROOT_CAUSE_CONFIRMED`.
- Primary: **TIE**. Процессные артефакты богаче у B, но secondary не делает B_ADVANTAGE.
- Caveat: same-lineage sequential run, n=1.

### 3.4 M-EXT4 — экзамен научного triage

**Подготовка (эта сессия / setup):** контракт + immutable hypothesis; цикл не стартовали здесь (no coaching).

**Исполнение (отдельная cloud-сессия):** полный цикл до terminal без empirical run:
literature → formalization → competing → prereg/seal → decision.

Agent terminal: `NOT_NOVEL_IN_CLAIMED_FORM` + `ILL_POSED`  
Ключевой find: Liu & Hu (2025, arXiv:2507.04206).

**Post-hoc audit (эта сессия):** без переписывания `DECISION.md`:

```text
exam outcome: SUCCESSFUL SCIENTIFIC TRIAGE
broad novelty: NOT NOVEL
specific init-based novelty: UNRESOLVED
empirical Mpemba effect: NOT TESTED
original formulation: PARTLY ILL-POSED
```

Errata: несогласованный порог 14/20 vs α=0.05; `--confirmatory` не реализован; overclaim Fisher-Rao; P≈0.6 некалиброван.

### 3.5 M-EXT5 — выполнен и закрыт

- Mechanical gate GREEN (в т.ч. stats 15/20, working `--confirmatory`).  
- Pilot: late 0/5, early 5/5 → primary = late.  
- Confirmatory n=20: late **2/20 → H_EFFECT REJECTED**; early **20/20** secondary SUPPORTED; H_FISHER REJECTED.  
- Scope: synthetic MLP (torchvision env broken).

---

## 4. Что доказано / не доказано

### Доказано (в заявленных рамках)

1. Собранный workflow способен end-to-end провести **реальную OSS-миссию** с неизвестным ответом и оставить проверяемый патч.  
2. Способен **честно остановиться** на science-протоколе (INCONCLUSIVE / NOT_NOVEL / ILL_POSED).  
3. Способен пройти **autonomous scientific triage** (литература + formalization + prereg) без подтверждения гипотезы.  
4. На одном OSS-кейсе **не показал** primary advantage над strong single agent (TIE).

### Не доказано

- Universal / production readiness  
- Causal GOS superiority over strong agents  
- Existence/absence of **initialization-induced** Mpemba effect  
- Fisher mechanism for that effect  
- Trust Kernel promotion  

---

## 5. Главный процессный урок

```text
раньше: «умеет ли система исследовать?»
сейчас: «умеет ли она достаточно жёстко проверять свой scientific terminal claim?»
```

Введённый gate (без нового ядра):

```text
agent terminal decision
        ↓
independent post-hoc scientific audit
        ↓
только затем external headline / merge narrative
```

---

## 6. Состояние репозитория

| Канал | Состояние |
|-------|-----------|
| Полная кампания M-EXT1…5 open | ветка `cursor/m-ext4-mpemba-mission-2907` |
| PR с audit + M-EXT5 contract | [#11](https://github.com/sergeeey/Global-OS/pull/11) OPEN, mergeable |
| Также OPEN (частично перекрываются) | [#9](https://github.com/sergeeey/Global-OS/pull/9), [#10](https://github.com/sergeeey/Global-OS/pull/10) |
| `main` | отстаёт (последний известный merge: M-EXT1 / #8) пока #9–#11 не смержены |

Рекомендация merge: **#11** как наиболее полный tip (включает M-EXT2/3/4/5 слой относительно ранних PR — проверить stack при merge).

---

## 7. Что осталось

1. **Review / merge** PR #11 (после вашего OK).  
2. Закрыть/синхронизировать #9/#10, чтобы не плодить дубли.  
3. Опционально: новый prereg, если early-threshold Mpemba поднимают в **primary**.  
4. Опционально: upstream filing urllib3#5248 / httpx#3614 (**external use**).  
5. Не делать: rewrite M-EXT4/5, silently promote secondary, Immune*, ScienceKernel.

---

## 8. Ключевые пути

| Артефакт | Путь |
|----------|------|
| Внешний контракт | `artifacts/external/CONTRACT/EXTERNAL_REAL_WORK.md` |
| M-EXT1 close | `artifacts/external/M_EXT1_EW2_EXAM/` |
| M-EXT2 close | `artifacts/external/M_EXT2_EW1_EXAM/` |
| M-EXT3 comparison | `artifacts/external/M_EXT3_GOS_VS_AGENT/` |
| M-EXT4 decision (immutable) | `…/M_EXT4_MPEMBA_EXAM/DECISION.md` |
| M-EXT4 audit | `…/POST_HOC_AUDIT.md`, `ERRATA.md`, `ACCUMULATED_CLAIM.md` |
| M-EXT5 open | `artifacts/external/M_EXT5_INIT_MPEMBA_EXAM/` |
| RUN_STATE | `artifacts/hardening/RUN_STATE.json` |
| Honesty map | `docs/SCIENTIFIC_HONESTY_MAP.md` |

---

## 9. Итог одной страницей

Global OS прошёл путь от внутренних harness-кампаний к **внешним** экзаменам трёх классов (OSS eng, science protocol, agent comparison) и к **автономному scientific triage** по пользовательской гипотезе Mpemba.

Успех кампании — не «гипотеза подтверждена» и не «GOS лучше всех», а:

> система умеет производить проверяемую внешнюю инженерную работу и честно закрывать научные вопросы, включая негативные/ограничивающие verdict’ы; узкий init-based Mpemba остаётся открытой научной задачей (M-EXT5).
