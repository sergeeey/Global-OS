# R2-HDE — Hypothesis Discovery Engine Report

**Mission class:** R2 (different from R1 honesty audit)  
**Engine mode:** Hypothesis Discovery Engine (12-step)  
**Search exhaustiveness:** NOT claimed  
**Generated:** 2026-09-25  

---

## Выбор объекта запуска (вход)

| Поле | Значение |
|------|----------|
| **Исходная гипотеза** | После того как короткие controlled A/B показывают **отсутствие** прироста primary sealed/reliability метрик у GOS vs сильный baseline, GOS research-loop (goal contract → competing hypotheses → falsification → durable trail → terminal) всё равно повышает **operator-kept useful remediations per human intervention** на реальных engineering/integrity миссиях относительно unconstrained strong-agent работы на тех же миссиях. |
| **Область** | LLM agents / agent scaffolding / evaluation methodology / autonomous research systems (определено самостоятельно как максимальный leverage после Y20–Y22/R1) |
| **Практическое решение** | Продолжать R2+ real-use инвестиции vs вернуться к synthetic A/B / поставить на паузу |
| **Ограничения** | Открытый веб + артефакты репо; языки EN(+RU вторично); период приоритета 2009–2026 (checklists) и 2023–2026 (agents); время ~1 сессия; бюджет = web search + локальные факты; без выдуманных публикаций |

**Почему эта гипотеза, а не Y23:** она отвечает на уже заданный практический вопрос кампании и не является sealed-metric fishing.

---

## 1. Краткий вывод

- **Поддержка H:** слабая–умеренная на уровне *аналогий и кампанийных process-фактов*; **нет** независимого controlled A/B по метрике «useful remediations / intervention».
- **Противоречия:** сильные — Agentless / DirectSolve / CCI / Reflexion-WebShop показывают, что **сложный агентный scaffolding часто не бьёт** сильный простой baseline по primary task success; иногда вредит.
- **Границы:** если «ценность» = sealed/task success — H плохо поддержана (Y20–Y22 + внешняя литература). Если «ценность» = auditability / keepable trail / low intervention на real integrity work — H **открыта** и совместима с R1, но не доказана сравнительно.
- **Самый перспективный пробел:** **discriminating A/B на ≥3 real missions** с pre-registered primary = `operator_kept_artifacts / (1 + interventions)` при equal model pin и caps — vs unstructured strong agent.

---

## 2. Формализованная гипотеза

### Атомарные утверждения

| ID | Утверждение |
|----|-------------|
| A1 | На short controlled sealed/reliability задачах GOS не даёт primary gain vs strong baseline. |
| A2 | GOS-loop принуждает к goal contract, competing hypotheses, falsification, durable trail, terminal stop. |
| A3 | A2 повышает долю *operator-kept* артефактов/фиксов на real missions. |
| A4 | A2 снижает число human interventions на ту же полезную работу. |
| A5 | Отношение keepable_output / interventions выше у GOS, чем у unconstrained strong agent при equal model+caps. |
| A6 | Эффект A5 держится, даже когда primary science/reliability scores tied/null. |

### Причинная цепочка

```text
GOS process constraints (A2)
  → richer falsification + durable evidence trail
  → fewer silent dead-ends / overclaims
  → more operator-kept remediations per intervention (A5)
  при условиях:
    D: real mission с неизвестным исходом (не toy sealed probe)
    E: equal model pin + budgets
    F: primary success ≠ sealed exact-match (или sealed уже null)
```

### Скрытые допущения

- «Operator-kept» измерим и стабилен между операторами.
- Unconstrained strong agent — валидный counterfactual (не намеренно ослаблен).
- Trail richness не путается с полезностью (secondary ≠ primary).
- Generator/authorship contamination не объясняет R1 keepability.

### Многозначные термины

- **GOS / scaffolding** — OS invariants vs prompt loop vs multi-agent.
- **Autonomy** — interventions vs unsupervised wall-time vs tool freedom.
- **Usefulness** — mergeable fix vs interesting notes vs science score.
- **Strong baseline** — Agentless-style pipeline vs free agent vs same model no loop.

### Проверяемые предсказания

| Если H верна | Не должно | Ослабит | Опровергнет | Нужны данные |
|--------------|-----------|---------|-------------|--------------|
| Keep-rate GOS > baseline при tied science | GOS всегда выше sealed scores | Keep-rate ≈; interventions ↓ только за счёт недоделки | Keep-rate GOS ≤ baseline при equal caps на ≥3 миссиях | paired missions + pre-reg rubric |
| Interventions GOS ≤ baseline при той же keep | Interventions GOS ≫ при той же keep | Cost GOS ≫ без keep gain | Cost-normalized utility GOS хуже | tokens/tools/wall + keep labels |
| Falsified nulls сохранены в trail | Nulls исчезают / переписываются | Trail есть, keep нет | Trail fabricated / unscorable | artifact audit |

---

## 3. Карта доказательств

| Утверждение | Поддержка | Противоречия | Условия | Качество | Источники |
|---|---|---|---|---:|---|
| A1 short A/B primary null | Y20 A≥B; Y21/Y22 TIE | — | sealed/reliability probes; shared generator caveat | 0.7 campaign | `artifacts/y20|y21|y22/*`; prereg SHAs |
| A2 GOS loop components used | Y19–Y22/R1 process logs | «GOS» может быть только prompt ritual | dogfood missions | 0.6 | process_log / GOAL_CONTRACT |
| A3 keepable remediations | R1: matrix path bind + regression kept | n=1 mission; no paired baseline arm | honesty/evidence class | 0.4 | `artifacts/r1/` |
| A4 fewer interventions | R1 interventions=0 | no counterfactual arm | same | 0.3 | `artifacts/r1/process_log.json` |
| A5 ratio advantage | — | Agentless > complex agents on SWE-bench Lite (32%, $0.70); DirectSolve > scaffolding matched-LLM; CCI all-in worse | SWE / QA / coding benches ≠ GOS integrity missions | 0.75 external against *task-success* reading of H | Xia et al. Agentless arXiv:2407.01489 (2024); LCLM DirectSolve arXiv:2505.08120 (2025); CCI arXiv:2605.05716 |
| Scaffolding helps coding | Reflexion HumanEval gains | WebShop: no improvement, early stop; reproduction WebShop success often ~0–13% modern models | task-dependent; env feedback quality | 0.55 mixed | Shinn et al. Reflexion NeurIPS 2023 arXiv:2303.11366; GitHub ReAct#34 |
| Process discipline helps safety domains | WHO checklist: mortality 1.5%→0.8%, complications 11%→7% (Haynes 2009) | before-after confounding; meta-analyses AMSTAR confidence often critically low; high I² | hospitals / surgery ≠ LLM agents | 0.5 analogy | Haynes et al. NEJM 2009; Bergs et al. BJS 2014 meta; Abbott et al. BJA 2018 |
| Capability threshold for scaffolds | MAS scaling: architecture helps only above model capability floor | — | terminal eng. tasks; 2026 preprint | 0.45 early | arXiv:2607.27942 |
| Forced durable summaries | help weaker model / hard task | hurt strong model on easy oracle (−35%, p=0.0006) | SynthOracle; n=5 seeds | 0.5 | Zenodo 10.5281/zenodo.19666413 (2026) |

---

## 4. Конкурирующие объяснения

| Гипотеза | Что объясняет | Слабые места | Различающий тест |
|---|---|---|---|
| **H (GOS usefulness under null science)** | R1 keep + rich trails при Y20–Y22 null | нет paired baseline; selection of mission class | R2 A/B real missions, primary=keep/intervention |
| **Halt1 Model-capacity** | Gains/ties = model pin equality; scaffolding irrelevant | не объясняет systematic richer B traces | same scaffold, vary model size |
| **Halt2 Process-as-tax** | richer trail = cost without keep gain; Agentless/DirectSolve | не объясняет R1 keep if unstructured would thrash | cost-normalized keep; Agentless-style vs GOS on same mission |
| **Halt3 Hawthorne / operator-alignment** | checklist-like gains from being watched / writing claims | hard to blind | third-party evaluators; pre-committed keep rubric |
| **Halt4 Contamination** | R1 author also wrote generator/tests | Y20–Y22 already flagged | independent operator mission + held-out repo area |

---

## 5. Междисциплинарные мосты

| Область | Структурная аналогия | Переносимый метод | Ограничение | Проверка |
|---|---|---|---|---|
| Хирургические checklists | forced process → fewer silent omissions → outcome | pre-reg checklist + adherence audit | mortal outcomes ≠ code keep; confounding | adherence×keep interaction on R2 |
| Aviation CRM | brief→execute→debrief trail | mandatory null recording | regulated vs research agents | force null-result files; count reopen rate |
| Clinical trial CONSORT | prereg + primary endpoint discipline | lock primary before unseal (уже Y20–Y22) | science endpoint ≠ usefulness | lock usefulness primary for R2 |
| Software pipelines (Agentless) | fixed phases beat free agent | localization→repair→validate | may underfit open research | Agentless-counterpart for integrity missions |

Структура процесса (не термины):  
`скрытое состояние качества работы → шумные действия агента → обязательная фиксация гипотез/нулей → обнаружение overclaim → keep/reject`

---

## 6. Найденные пробелы

Веса итоговой оценки — **рабочие**, не научные константы:  
`0.25·rel + 0.15·qual + 0.20·nov + 0.15·inter + 0.15·fals + 0.10·crit − redun`

| Пробел | Тип | Потенциал | Проверяемость | Итог |
|---|---|---:|---:|---:|
| Нет paired real-mission A/B по keep/intervention | отсутствие данных | 0.9 | 0.8 | **0.78** |
| Нет калибровки «operator-kept» между людьми | отсутствие измерения | 0.7 | 0.7 | 0.62 |
| Неизвестно: GOS vs Agentless-style fixed pipeline на integrity | непроверенная связь | 0.75 | 0.75 | 0.70 |
| Mechanism: trail → keep causal? | отсутствие причинного объяснения | 0.65 | 0.5 | 0.55 |
| External nulls on scaffolding vs our R1 keep | противоречие уровней метрик | 0.8 | 0.6 | 0.66 |
| Transfer checklist adherence metrics to agents | междисциплинарный перенос | 0.55 | 0.6 | 0.52 |

---

## 7. План проверки

### 1 день
- Pre-register R2-A/B protocol: primary = keep_rate / (1+interventions); secondary = trail completeness, cost.
- Pick 1 small real mission (e.g. flake hunt / docs honesty in held-out package).
- Run Arm A unstructured; freeze; Arm B GOS; independent keep labels.
- **Success:** protocol executable end-to-end. **Falsify H early if** B keep≤A and interventions≥A.

### 1 неделя
- N=3 missions, different classes; same model pin; locked rubric.
- Include Agentless-style fixed-phase arm as Halt2 control if capacity.
- Cost: tokens/tools/wall.
- **Success:** B wins primary on ≥2/3 with MCID pre-set. **Reject H if** B never wins primary.

### Полноценное исследование
- N≥10 missions; two operators for keep IRR; holdout missions; optional model-size split (Halt1).
- Publish negative results; no post-hoc primary swap.
- Complexity/cost ~8/10.

---

## 8. Нерешённые вопросы

- Каузален ли GOS-loop для R1 keep, или достаточно любого disciplined prompt?
- Переносится ли Agentless-урок на research/integrity, или только на SWE-bench localization?
- Как измерять keep без circularity (автор миссии ≠ оценщик)?
- Порог capability, выше которого durable summaries вредят (SynthOracle pattern)?
- Нужен ли T0/T1 OS для process gains, или хватает eval harness? (ADR-0009 relevant)
- WebShop reproduction collapse: насколько published agent gains fragile?

---

## 9. Итоговая калибровка

`<fact>` Y20–Y22: primary GOS sealed/reliability advantage NOT SHOWN; process traces richer under B. R1: terminal SUPPORTED, interventions=0, trunk kept path-bindings + lint. Agentless (arXiv:2407.01489): simple pipeline beat complex open-source agents on SWE-bench Lite at lower cost. Haynes 2009: checklist associated with mortality/complication drops in before-after design.

`<inference>` If «GOS value» is defined as sealed primary success, current evidence favors **not investing** in more short A/B. If defined as keepable real-use under null science scores, evidence is **compatible but underdetermined**; external literature warns scaffolding often fails on task success — so R2 must not smuggle task-success as proxy.

`<hypothesis>` **H_R2:** On real integrity/engineering missions with equal model+caps, GOS-loop raises `operator_kept / (1+interventions)` vs unstructured strong agent even when sealed probes stay null. **H_R2b:** Fixed-phase Agentless-style pipeline matches GOS keep at lower cost (Halt2 wins). **H_R2c:** Durable forced summaries help only when model-task gap is large (capability-threshold).

`<unknown>` Paired counterfactual for R1; IRR of keep labels; whether OS kernel (vs ritual) is necessary; true effect size of H_R2.

`<confidence>` **0.38** for H as stated (directional plausibility from R1 + analogies; strong external pressure against scaffolding-as-universal-win; no discriminating experiment yet). Confidence that **Y23 is the wrong next move:** **0.72**.

---

## Knowledge graph (compact)

```text
A1_null_science --поддерживает--> pivot_to_real_use
A1_null_science --противоречит--> invest_in_Y23
Agentless_win --противоречит--> "more agent = better task success"
Agentless_win --является_аналогом--> Halt2_fixed_pipeline
CCI_interference --ограничивает--> unbounded_scaffold_stacking
Reflexion_mixed --работает_только_при--> strong_env_feedback
Checklist_analogy --является_аналогом--> GOS_process_discipline
Checklist_analogy --не_работает_при--> equating_to_causal_proof_for_agents
R1_keep --поддерживает--> H_R2 (weak, n=1)
R1_keep --зависит_от--> no_paired_baseline
H_R2 --измеряет--> keep/(1+interventions)
H_R2 --объясняется_альтернативно--> Halt1|Halt2|Halt3|Halt4
```

## Источники (ключ; не исчерпывающе)

1. Xia et al., Agentless, arXiv:2407.01489, 2024; FSE/PACMSE 2025 DOI 10.1145/3715754 — SWE-bench Lite 32%/ $0.70.  
2. Putting It All into Context (DirectSolve), arXiv:2505.08120, 2025.  
3. Shinn et al., Reflexion, NeurIPS 2023, arXiv:2303.11366.  
4. ReAct WebShop reproduction issue: https://github.com/ysymyth/ReAct/issues/34  
5. More Is Not Always Better (CCI), arXiv:2605.05716.  
6. Scaling LLM-Driven MAS, arXiv:2607.27942.  
7. Structured Reasoning… Scaffolding Not Regularization, Zenodo 10.5281/zenodo.19666413, 2026.  
8. Haynes et al., NEJM 2009;360:491–499.  
9. Bergs et al., BJS meta-analysis DOI 10.1002/bjs.9381.  
10. Campaign: `artifacts/y20|y21|y22|r1/`.  

Первичные PDF/HTML частично доступны через fetch; где мета-анализы за paywall — отмечено ограничение доступа к полному тексту.
