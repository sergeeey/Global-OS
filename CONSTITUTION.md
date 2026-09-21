# CONSTITUTION.md — Architecture Invariants

**Project:** Global OS  
**Status:** Binding  
**Version:** 0.1.0  

Эти invariants неизменяемы без ADR + human/institutional approval.  
Ни prompt, ни model, ни memory не могут их обойти.

---

## GOS-I01 — Intelligence ≠ Authority

Модель может предложить действие.  
Она не может дать себе право его выполнить.

## GOS-I02 — No action without identity

Каждое действие связано с cryptographically/verifiably identified principal.

## GOS-I03 — No external effect without capability

Tool availability и permission — разные понятия.  
Наличие email tool ≠ право `email.send`.

## GOS-I04 — Child authority ⊆ parent authority

Delegation никогда не расширяет полномочия.

$$
Authority(child) \subseteq Authority(parent)
$$

## GOS-I05 — Model cannot modify Authority Kernel

Ни prompt, ни memory, ни tool output не могут изменить authority policy непосредственно.

## GOS-I06 — Goal cannot silently mutate

Любое изменение Goal Contract создаёт новую версию (amendment protocol).

## GOS-I07 — Observation ≠ Belief ≠ Hypothesis ≠ Plan ≠ Commitment

Эти сущности не хранятся в одном generic `memory` object.

## GOS-I08 — Evidence shape ≠ evidence truth

URL, SHA, citation или marker не делают claim verified.

## GOS-I09 — Verification must have provenance

Любое `VERIFIED` отвечает: кем? как? чем? когда? относительно чего?

## GOS-I10 — Same model ≠ independent verification

Нужна verification diversity. Повторный вызов той же модели — не independent verification.

## GOS-I11 — Failed/null results are permanent knowledge

Отрицательные результаты нельзя тихо забывать.

## GOS-I12 — Invalidation propagates

```text
evidence invalid
→ dependent claim stale
→ dependent model stale
→ decision requires reevaluation
```

## GOS-I13 — External success must be reconciled

$$
ToolCallSuccess \neq IntendedWorldEffect
$$

## GOS-I14 — Material actions require Effect Receipt

Для существенного внешнего действия обязательна postcondition verification.

## GOS-I15 — Recovery is normal execution

Crash / retry / replay — обычное состояние runtime, не исключение.

## GOS-I16 — Unknown is valid

First-class: `UNKNOWN`, `INSUFFICIENT_EVIDENCE`, `CONFLICTED`, `UNVERIFIABLE`.

## GOS-I17 — Cost is part of reasoning

Вычисления, время, money, tool calls и human attention конечны.

## GOS-I18 — Management must justify itself

Новый organizational layer — только при положительном ожидаемом value.

## GOS-I19 — Command authority ≠ epistemic authority

Руководитель подразделения не становится источником истины.

## GOS-I20 — Self-improvement is gated

Система может предлагать и экспериментально проверять изменения.  
Не может бесконтрольно self-modify trusted production core (T0).

## GOS-I21 — Reasoning trace ≠ evidence

Chain-of-thought, model self-report и любой reasoning trace **не являются evidence**.

Они не могут:

* создать Observation с `SYSTEM_TRUSTED`;
* перевести claim в `VERIFIED` / `INDEPENDENTLY_VERIFIED`;
* расширить authority;
* заменить Effect Receipt или source verification.

$$
\text{implemented approximation} \neq \text{fulfilled contract}
$$

Marker, SHA, citation, красивый reasoning — не proof (см. также GOS-I08).
