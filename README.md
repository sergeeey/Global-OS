# Global OS

**Durable Cognitive Runtime / Autonomous Work Operating System**

Global OS принимает от человека или организации **результат, ограничения, полномочия и критерии успеха** — и самостоятельно ведёт длинную работу: декомпозиция, организация, evidence, verification, recovery.

LLM **не** является архитектурным ядром. Модели — interchangeable compute за adapter boundary.

$$
\text{GlobalOS} =
\text{GoalContract} +
\text{EpistemicKernel} +
\text{DurableRuntime} +
\text{AuthorityKernel} +
\text{DynamicCognitiveOrganization} +
\text{EnvironmentCompiler} +
\text{WorldInteraction} +
\text{VerificationFabric} +
\text{AdaptiveLearning}
$$

## Статус

Milestone: **M1.5 CLOSED_SCOPE_LIMITED**; M2 CLOSED on current evidence.
PREPROD_V0_1 + CTC v0 are merged on `main`; pre-production release **NOT DECLARED**.
DoD v0.1 **не** claimed complete; `v0.1.0-pre` **not accepted**; `RELEASE_GATE` 0/10; `PRODUCTION_PROVEN=0`; `CONTINUAL_SI=NOT_MEASURED`. Evidence: `docs/capability_matrix.json`, `docs/IMPLEMENTATION_STATUS.md`.

Правило:

$$
\text{implemented approximation} \neq \text{fulfilled contract}
$$

См. [ROADMAP.md](ROADMAP.md), [CONSTITUTION.md](CONSTITUTION.md), [SPEC.md](SPEC.md).

## Быстрый старт

```bash
pip install -e ".[dev]"
make check

# создать Goal Contract (killer use case: repo audit)
gos goal create examples/goal_repo_audit.json
gos goal show goal_repo_audit_001
gos events tail --goal-id goal_repo_audit_001
gos audit .

# PREPROD_SUPERVISED: Goal → Gateway observe → Achiever → delivery
gos mission start --goal examples/goal_repo_audit.json --target . --budget-usd 15
gos mission status
gos mission deliver
```

Локальное состояние CLI пишется в `.gos/` (не production store).
Operator guide: [artifacts/preprod/OPERATOR.md](artifacts/preprod/OPERATOR.md).
Challenge-GA остаётся `NOT_STARTED` без отдельного разрешения.

## Принцип разработки

```text
Problem → Contract → Invariant → Tests → Implementation → Runtime evidence
```

Не начинать feature с prompt или Python class в обход schema/events.

## NON-GOALS

См. [NON_GOALS.md](NON_GOALS.md).

## Coding agents

См. [AGENTS.md](AGENTS.md). Перед любым изменением — `CONSTITUTION.md`.
