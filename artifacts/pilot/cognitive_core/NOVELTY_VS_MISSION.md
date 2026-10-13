# Novelty vs mission — working stance

**Status:** Binding for prioritization  
**Source:** literature-overlap review (supporting; not exhaustive) + Cognitive Core paradigm

## Priorities

| Priority | Focus | Budget |
|----------|-------|--------|
| **P0** | Cognitive Organs → Challenge-GA (goal achievement) | Main engineering |
| **P1** | Reliability substrate hardening (Authority, EffectReceipt, Verification Router) using external analogs as **checklists**, not as novelty claims | Spot checks |
| **P2** | Scientific novelty of individual mechanisms | Research only; never blocks P0 |

## Do not claim uniqueness for

Authority≠Intelligence · action-bound tokens · EffectReceipt · correlated-error awareness  
Treat as known principles; differentiate on **integration into Autonomous Goal Achiever**.

## External analogs (engineering samples — verify before adopting)

- SentinelAgent / CapLease — capability lease / one-shot grants  
- Praxa — world-effect confirmation patterns  
- Builder / Defender / Breaker — independence of verification from executor  

Do not treat these as proven optima without source + reproduction.

## Verification Router finding (2026-10-12)

On tip before fix: `HUMAN` tier could `passed=True` via numeric dual-deterministic stack
**without** `human_reference` — tier was a **label upgrade**, not stronger evidence (GOS-I08).

Mitigation: `VerificationRouter` fail-closes HUMAN without `human_reference`
(`tests/test_verification.py::test_human_tier_does_not_pass_by_label_alone`).

## Organ selection (mission-first addendum)

Each Cognitive Organ must select actions that advance the Goal — not busywork:

| Organ | Selection rule |
|-------|----------------|
| Decomposer | Q-D6 `task_advances_criteria` / phase mapping |
| Pivot/Replan | Q-P6 cite `why_failed` → exclude approach → new strategy |
| Orchestration | Q-O6 why tool/model, alternatives, `on_failure` → Pivot |

Path after this check: **DurableRunner (done) → Cognitive Organs → Challenge-GA**.
