# Отчёт: внешняя экзаменационная кампания Global OS

**Дата:** 2026-10-02 (honesty sync)  
**Ветка:** `cursor/m-ext4-mpemba-mission-2907` @ tip (см. git)  
**Sprint:** `M_EXT5_CLOSED`  
**Архитектура Global OS:** без изменений ради optics (ADR-0009 соблюдён)

---

## 0. Accumulated claim (канон)

> **Global OS способен автономно доводить реальные инженерные и научные миссии до проверяемого terminal outcome. В конкретном synthetic-MLP эксперименте поздний initialization-Mpemba effect не подтвердился, ранний crossing наблюдался как secondary result, а Fisher-механизм не подтвердился. Преимущество Global OS над сильным одиночным агентом пока не показано.**

Единый статус M-EXT5:

```text
M-EXT5 = CAMPAIGN_CLOSED
H_EFFECT(primary late) = REJECTED
H_FISHER = REJECTED
early crossing = SECONDARY SUPPORTED
fidelity/scope = synthetic MLP
```

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
| **M-EXT4 / EW4** | Science triage | Agent: `NOT_NOVEL`+`ILL_POSED`; Audit: **SUCCESSFUL TRIAGE** | Автономный triage; эмпирика тогда ещё не бежала |
| **M-EXT5 / EW5** | Science (residual) | **CAMPAIGN_CLOSED** | Late H_EFFECT REJECTED; early secondary SUPPORTED; H_FISHER REJECTED; synthetic MLP |

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

Agent terminal (immutable): `NOT_NOVEL_IN_CLAIMED_FORM` + `ILL_POSED`  
Ключевой find: Liu & Hu (2025, arXiv:2507.04206).

Post-hoc audit (исторический snapshot на момент triage, до M-EXT5):

```text
exam outcome: SUCCESSFUL SCIENTIFIC TRIAGE
broad novelty: NOT NOVEL
specific init-based novelty: UNRESOLVED   ← тогда; см. M-EXT5 ниже
empirical Mpemba effect: NOT TESTED       ← тогда; см. M-EXT5 ниже
original formulation: PARTLY ILL-POSED
```

Errata M-EXT4: порог 14/20 vs α=0.05; `--confirmatory` не работал; overclaim Fisher-Rao; P≈0.6 некалиброван.

### 3.5 M-EXT5 — CAMPAIGN_CLOSED

```text
M-EXT5 = CAMPAIGN_CLOSED
H_EFFECT(primary late, loss≤0.35) = REJECTED          (2/20)
H_FISHER = REJECTED
early crossing (secondary, loss≤1.0) = SUPPORTED_WITHIN_SCOPE  (20/20)
fidelity/scope = synthetic MLP (CPU)
mechanical gate = GREEN; stats rule = 15/20
```

- Pilot: late 0/5, early 5/5 → primary locked to **late**.  
- Confirmatory sealed n=20.  
- Early secondary **не** поднимается в headline primary без нового prereg.

---

## 4. Что доказано / не доказано

### Доказано (в заявленных рамках)

1. Workflow способен end-to-end провести **реальную OSS-миссию** с неизвестным ответом и оставить проверяемый патч.  
2. Способен **честно остановиться** на science-протоколе (INCONCLUSIVE / NOT_NOVEL / ILL_POSED / REJECTED).  
3. Способен пройти **autonomous scientific triage** и довести residual empirics до dual terminal.  
4. На одном OSS-кейсе **не показал** primary advantage над strong single agent (TIE).  
5. **В этом synthetic-MLP протоколе:**
   ```text
   Late initialization-induced Mpemba effect: REJECTED
   Early threshold-dependent crossing: SUPPORTED as secondary
   Fisher mechanism: REJECTED in this protocol
   ```

### Не установлено / не переоценивать

```text
General existence/absence of init-Mpemba across neural networks / LR regimes:
  NOT ESTABLISHED
Causal GOS superiority vs strong agents: NOT SHOWN
Universal / production readiness: NOT SHOWN
Trust Kernel promotion: NO
```

Нельзя говорить «existence/absence init-Mpemba вообще неизвестны» после M-EXT5: **late-эффект в этом протоколе уже REJECTED**; неизвестна лишь **генерализация**.

---

## 5. Главный процессный урок

```text
раньше: «умеет ли система исследовать?»
сейчас: «умеет ли она достаточно жёстко проверять свой scientific terminal claim?»
```

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
| Канонический tip кампании | `cursor/m-ext4-mpemba-mission-2907` → PR **#11** |
| Ancestry | tip **#9** (`cb05dad`) и tip **#10** (`3308087`) — **ancestors of #11** (`46ef3c1`) |
| #9 / #10 | OPEN duplicates — закрыть после merge #11 |
| `main` | отстаёт (последний merge: #8 / M-EXT1) |

Рекомендация: **merge #11** → close #9 и #10 → `main` = единственная каноническая истина.

---

## 7. Что дальше (не M-EXT6)

1. Merge #11; закрыть дубли #9/#10.  
2. **Не** поднимать early-Mpemba secondary в primary без отдельного prereg.  
3. **Не** запускать цепочку новых экзаменов ради самооценки.  
4. Перейти к **pilot usage** на реальных задачах пользователя:

```text
большая задача
→ Goal Contract
→ автономное исследование/разработка
→ competing alternatives
→ experiments / implementation
→ independent audit
→ deliverable
```

Собирать естественные наблюдения (где нужен человек, ошибки, recovery, неподтверждённые claims, время, внешний результат, сравнение со strong agent).  
Архитектуру менять только от **повторяющихся** реальных failures.

5. Опционально: upstream urllib3#5248 / httpx#3614 (**external use**).

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
| M-EXT5 **CLOSED** | `artifacts/external/M_EXT5_INIT_MPEMBA_EXAM/` (`DECISION.md`, `M_EXT5_CLOSED.json`) |
| RUN_STATE | `artifacts/hardening/RUN_STATE.json` |
| Honesty map | `docs/SCIENTIFIC_HONESTY_MAP.md` |

---

## 9. Итог

Инфраструктуры достаточно, чтобы **работать**. Главная работа Global OS теперь — не доказывать, что он существует, а приносить реальные результаты пользователю.
