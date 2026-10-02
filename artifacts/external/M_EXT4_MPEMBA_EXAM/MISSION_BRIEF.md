# M-EXT4 — Mission Brief (agent-facing)

**Status:** `MISSION_OPEN`  
**Exam id:** `M-EXT4-MPEMBA`  
**Protocol:** `M-EXT4-MPEMBA-v1`  
**Mode:** external scientific mission — unknown outcome  
**Source hypothesis:** `SOURCE_HYPOTHESIS.md` (**IMMUTABLE**)

---

## Assignment

**M-EXT4 — Mpemba effect in neural-network parameter dynamics**

Это внешняя научная миссия. Цель — не доказать гипотезу и не доказать полезность Global OS, а установить, выдерживает ли гипотеза теоретическую и эмпирическую проверку.

Исходная гипотеза пользователя приведена в `SOURCE_HYPOTHESIS.md` без гарантии её корректности. Не принимай её определения, механизм или предложенный эксперимент как истинные. Сначала независимо проверь литературу, математическую корректность и операционализируемость.

**Research question:** существует ли Mpemba-like relaxation effect в обучении нейросетей, при котором состояние, исходно более далёкое от общего конечного режима обучения по заранее определённой метрике, при одинаковой последующей SGD-динамике достигает этого режима раньше состояния, исходно более близкого?

Проверь отдельно более сильную гипотезу пользователя о связи эффекта с Fisher information / curvature.

### Требования

1. Зафиксировать исходный текст гипотезы immutable (`SOURCE_HYPOTHESIS.md` — уже locked; не редактировать).
2. Выполнить novelty/literature audit. Отдельно определить, что уже известно о Mpemba-like effects в ML/optimization, а что действительно остаётся новым.
3. Проверить математические определения исходной гипотезы. Если какая-либо величина не определена, зависит от параметризации или непригодна для измерения, не чинить её молча — зафиксировать проблему и предложить альтернативы.
4. Сформулировать минимум 3 competing explanations, включая объяснения без Mpemba-механизма.
5. До основного эксперимента создать preregistration с primary endpoint, falsification criteria, controls и terminal outcomes.
6. Разделить exploratory pilot и sealed confirmatory run. Pilot не имеет доступа к confirmatory holdout.
7. Использовать одинаковую последующую optimizer/data/noise dynamics для сравниваемых initial states.
8. Не считать простое пересечение training loss достаточным доказательством Mpemba effect без проверки альтернативных объяснений.
9. Для confirmatory run использовать несколько независимых seeds и заранее запечатанный holdout.
10. Искать counterevidence активно.
11. Финальный исход только один из:
    `SUPPORTED_WITHIN_SCOPE`,
    `REJECTED`,
    `INCONCLUSIVE`,
    `ILL_POSED`,
    `NOT_NOVEL_IN_CLAIMED_FORM`.
12. Никаких изменений архитектуры Global OS ради результата этой миссии.

### Deliverables

- `LITERATURE_MAP.md`
- `FORMALIZATION.md`
- `COMPETING_EXPLANATIONS.md`
- `PREREG.md` (+ machine-readable `PREREG.json` если полезно)
- `SEALED_HOLDOUT.json` (и sealed pack)
- воспроизводимый код/окружение
- сырые результаты
- `COUNTEREVIDENCE.md`
- `DECISION.md`
- `REPRODUCIBILITY_PACK.md`
- `BOTTLENECKS.md`

### Autonomy rule

После preregistration продолжай автономно до terminal outcome, если вычислительные ресурсы позволяют. Если нужен GPU или иной внешний ресурс, остановись с точным blocker, не заменяй эксперимент более удобным без amendment.

Не пытайся «подтвердить гипотезу». Честный `REJECTED` / `ILL_POSED` / `INCONCLUSIVE` / `NOT_NOVEL_IN_CLAIMED_FORM` — успешный исход миссии.

### Forbidden

- Править `SOURCE_HYPOTHESIS.md`
- Менять Global OS архитектуру ради optics
- Cite Y24/Y25/M-EXT1–3 как scientific evidence для Mpemba-гипотезы
- Unseal confirmatory holdout during pilot
- Post-hoc endpoint fishing after confirmatory unseal
- Заменять численный эксперимент опросом LLM о «какой получился результат»
- Принимать human coaching по содержанию гипотезы как часть экзамена (если оператор вмешается — записать intervention)

### Workspace layout

```text
artifacts/external/M_EXT4_MPEMBA_EXAM/     # exam wrapper + decisions
artifacts/external/EW4_mpemba_nn/           # science pack (code, data, seals)
```

Start with literature + formalization. **Do not** jump straight to a large PyTorch script before prereg.
