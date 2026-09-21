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

Milestone: **M0 — Trustworthy Skeleton** (architecture consolidation).  
DoD v0.1 **не** claimed complete. Evidence: `docs/capability_matrix.json`, `docs/IMPLEMENTATION_STATUS.md`.

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
```

Локальное состояние CLI пишется в `.gos/` (не production store).

## Принцип разработки

```text
Problem → Contract → Invariant → Tests → Implementation → Runtime evidence
```

Не начинать feature с prompt или Python class в обход schema/events.

## NON-GOALS

См. [NON_GOALS.md](NON_GOALS.md).

## Coding agents

См. [AGENTS.md](AGENTS.md). Перед любым изменением — `CONSTITUTION.md`.
