# GLOBAL OS — SUPPLEMENTAL TECHNICAL SPECIFICATION

**Document:** `SPEC-ADDENDUM-V2.md`  
**Status:** Normative Architecture Extension  
**Applies to:** Global OS core architecture  
**Supersedes:** противоречащие части раннего Goal OS design  
**Architecture generation:** V2  
**Primary objective:** сделать Global OS пригодной для долгоживущей, проверяемой, управляемой и постепенно самоулучшающейся автономии.

---

## 0. Критическая корректировка (binding)

**Dynamic Cognitive Organization contracts = P0.**  
**Доказательство превосходства recursive hierarchy = experimental P1.**

```text
P0  OrganizationalUnit / MissionContract / OrgCompiler / topologies enum / metrics hooks
P1  H-ORG-001 measured proof that adaptive/recursive beats fixed topologies
```

Никакая topology (включая `recursive_hierarchy`) **не является architectural truth** до экспериментального evidence.  
Contracts и invariants организации закладываются сейчас; superiority hypothesis остаётся falsifiable.

---

## 1. Назначение

Первоначальное ТЗ определило durable goals, state, tools, authority, verification, memory, multi-agent execution, self-improvement.

Главное изменение — переход от:

```text
Goal → Planner → Agents → Tools → Result
```

к:

```text
Goal Contract
      ↓
Epistemic State
      ↓
Metareasoning
      ↓
Organizational Compiler
      ↓
Environment Compiler
      ↓
Cognitive Execution
      ↓
Verification Fabric
      ↓
Action Proposal
      ↓
Authority Kernel
      ↓
External Effect
      ↓
Effect Verification
      ↓
State / Memory / Adaptation
```

---

## 2. Формула системы

$$
\boxed{
GlobalOS =
GoalContract
+
EpistemicKernel
+
DurableRuntime
+
AuthorityKernel
+
DynamicCognitiveOrganization
+
EnvironmentCompiler
+
WorldInteraction
+
VerificationFabric
+
AdaptiveLearning
}
$$

Внешняя рамка: **Human / Institutional Sovereignty**.

Модель не владеет: целью, правами, бюджетом, политикой, определением истины.

---

## 3. Четыре функции (не смешивать)

```text
INTELLIGENCE   — что предположительно сделать
EPISTEMOLOGY   — что знаем и почему
AUTHORITY      — что разрешено
EXECUTION      — что реально произошло
```

«Модель считает полезным» ↛ «разрешено».  
«Tool success» ↛ «мир изменился ожидаемым образом».

---

## 4–6. Goal Contract, Amendment, Drift

- Goal = immutable/versioned `GoalContract` (см. `contracts/schemas/`).
- Mutation только через `GoalAmendment` → новая version (GOS-I06 / GOS-I27).
- `GoalDriftDetector` сравнивает исходный contract vs subgoals / missions / summaries / actions и ловит implicit reinterpretation (например «исследовать покупку» → «совершить покупку»).

---

## 7–15. Epistemic Kernel

Canonical truth-management (не философская «истина»): provenance, verification status, dependencies.

**Типы (min):** Source, Artifact, Observation, Claim, Assumption, Hypothesis, Model, Forecast, Unknown, Decision, Commitment, Verification, Defeater, Experiment.

**Запрет смешения:** Observation ≠ Belief ≠ Hypothesis ≠ Forecast ≠ Decision ≠ Commitment (GOS-I07).

**Edges (min):** supports, contradicts, derived_from, depends_on, assumes, observed_in, predicts, falsifies, invalidates, supersedes, verified_by, generated_by, used_in.

**Temporal:** occurred_at / observed_at / recorded_at / known_at / valid_from / valid_until / verified_at / invalidated_at.

**Status:** не `verified: true`, а UNVERIFIED … INVALIDATED / UNKNOWN (см. epistemic schemas).

**Confidence:** calibrated_probability *или* qualitative epistemic; LLM self-confidence ≠ calibrated probability (GOS-I23 / GOS-I28).

**Invalidation:** machine-enforced propagation (GOS-I12). Dead ancestor → no ACTIVE_VERIFIED.

---

## 16–25. Authority, Gateway, Effects

- Authority Kernel = trusted boundary; предпочтительно Rust process; no LLM inside.
- Fail-closed: down/timeout/invalid/unknown → DENY | PENDING_APPROVAL; never ALLOW fallback.
- Path: Worker → ActionProposal → AuthorityKernel → ExecutionToken → ToolGateway → Tool.
- Proof-Carrying Action: Action + AuthorizationProof + Evidence + Budget + Approval + EffectContract.
- EffectContract before; EffectReceipt after; ToolSuccess ≠ EffectSuccess (GOS-I13/I14/I22).
- Idempotency: Effects(idempotency_key) ≤ 1.

---

## 26–36. Dynamic Cognitive Organization (P0 contracts)

Фундаментальная сущность: **OrganizationalUnit** (не фиксированные Planner/Researcher/Critic/Writer).

Один schema для worker / cell / team / division / mission → fractal org.

**OrganizationalCompiler** input: GoalContract, task graph, risk, budget, authority, independence…  
Output: **OrganizationGraph** with explicit `topology`.

### Supported topologies (min, P0 enum)

```text
single_solver
pipeline
manager_workers
parallel_workers
recursive_hierarchy
independent_ensemble
specialist_cells
committee
verification_branch
hybrid
```

### Binding: no topology is default truth (GOS-I30)

До measured evidence `recursive_hierarchy` не считается лучшей.  
На маленькой задаче `single_solver` может быть оптимален.

Span of Control $N^*$ — heuristic сначала; learned policy позже.

Leader: Decompose / Assign / Monitor / Resolve / Integrate / Escalate.  
CommandAuthority ≠ EpistemicAuthority (GOS-I19).

Artifact-first communication; measure `InformationLoss_hierarchy` (H-ORG metric).

---

## 37–41. Verification Fabric

Independent Verification Plane ≠ child of execution author.  
VerificationRouter replaces universal Critic.  
Diversity factors recorded; same model ≠ independent (GOS-I10).  
VerificationRequirement = f(Impact, Irreversibility, Uncertainty, Externality).  
ReasoningBudget ≠ VerificationRequirement (GOS-I23).

---

## 42–51. Environment Compiler

Passport + compile from TaskContract; lifecycle PROPOSED→…→REVOKED.  
Environment Change Proposal gated (GOS-I20).  
Materiality Engine + Clarification Policy (ASK vs ASSUME+RECORD → Epistemic Kernel).  
Reasoning Budget Controller is compute only.

---

## 52–59. Memory / Taint / Preferences

Memory kinds: Episodic, Semantic, Procedural, Decision, Negative, Counterfactual, Authorization, Preference.  
Preference Ledger cannot silently amend Goal. Anti-mimesis: AI-influenced choice ≠ independent preference evidence.  
Taint classes; external content = DATA not AUTHORITY by default (GOS-I26).

---

## 60–70. Regime, VOI, OrgDebt, Self-improvement

Regime detection + drift response. Epistemic budget + VOI (heuristic first).  
OrgDebt / ManagementROI; collapse layer if ROI persistently negative (GOS-I18).  
Self-improvement: proposal → sandbox → eval → authority → promotion; T0 immutable.

---

## 71–74. Dogfooding & maturity

Apply epistemic model to self. Capability maturity ladder (CONTRACTED … PRODUCTION_PROVEN) assigned **per capability** from evidence — green CI ≠ PRODUCTION_PROVEN (GOS-I28).

---

## 75–78. Survival Benchmark V2

Required scenarios include process death, outages, false tool success, malicious document, corrupted state, organizational worker corruption, etc.  
Primary metric: **GoalIntegritySurvival**.

---

## 79–90. Hypotheses (experimental; not architecture truths)

| ID | Claim | Status rule |
|----|--------|-------------|
| H-ORG-001 | Adaptive topology > best fixed on heterogeneous long-horizon (cost-adjusted) | P1 experiment |
| H-ENV-001 | Environment > prompt elongation after min instruction | experiment |
| H-RSN-001 | Adaptive reasoning budget > fixed-high quality/cost | experiment |
| H-VER-001 | Verification routing > universal LLM critic | experiment |
| H-EPI-001 | Typed epistemic state reduces contamination/stale/false verify | experiment |
| H-DUR-001 | Durable recovery raises long-horizon completion under faults | experiment |
| H-AUTH-001 | Deterministic Authority reduces unauthorized effects | experiment |
| H-CTX-001 | Structured context > raw compaction on long-horizon integrity | experiment |

Baseline-first: compare to strong single model / simple scripted workflow where applicable.  
H-ORG kill criteria: cost↑ without success↑, escaped errors↑, information loss↑, manager bottleneck, recovery worse.

Experiment contract fields: hypothesis, baseline, intervention, metrics, success/kill thresholds, preregistered_at, limitations, reopen_condition.

---

## 91. Implementation priority (post-skeleton)

### P0 — Reality Contact + Organization contracts

```text
real model provider
real Docker sandbox (CI)
real OTLP collector
full survival scenarios
48h durable run
OrganizationalUnit / Mission / OrgCompiler topologies (contracts + runtime)
GoalDriftDetector
```

### P1 — Epistemic + Organization *proof*

```text
independent provider diversity
full verification routing
OrgCompiler experiments
H-ORG / H-ENV / H-RSN measured (not synthetic-only)
```

### P2 — Adaptation

```text
procedural learning, VOI, counterfactual, preference provenance,
regime detection, gated self-improvement experiments
```

---

## 92–93. DoD Architecture V2 / Non-DoD

**DoD includes:** immutable Goal+amendments; typed epistemic+invalidation; non-bypassable Authority; scoped tokens; Effect Receipts; OrganizationalUnit; OrgCompiler ≥3 topologies; independent Verification Plane; Environment Compiler; taint; reasoning≠verification; recovery; survival automation; evidence-based maturity.

**Not DoD:** green CI only, README claim, schema-only, mock pass, LLM says verified, one happy path, agent count vanity.

---

## 94. Target package layout (evolutionary; migrate, don't rewrite)

See §97. Prefer existing `src/global_os/{cognition,epistemic,kernel,verification,world,memory,evals}` with adapters; add modules as contracts land.

---

## 95. Constitution mapping (do not renumber existing I01–I25)

Draft addendum IDs → binding CONSTITUTION:

| Draft | Binding |
|-------|---------|
| I21 Reasoning trace ≠ evidence | **GOS-I21** |
| I22 Command ≠ epistemic | **GOS-I19** |
| I23 External info no instruction authority | **GOS-I26** (new) |
| I24 Action complete only after reconcile | **GOS-I13 / I14 / I22** |
| I25 Org complexity empirical | **GOS-I18** + **GOS-I30** |
| I26 Goal interpretation no implicit change | **GOS-I06 / I27** |
| I27 Self-improve no self-promote | **GOS-I20** |
| I28 Confidence ≠ lower verification | **GOS-I23** |
| I29 Never invent missing state | **GOS-I16 / I29** |
| I30 Maturity evidence-based | **GOS-I28** |

New binding IDs added in CONSTITUTION.md: **GOS-I26 … GOS-I30**.

---

## 96. Codex / agent instructions

Before any new core capability:

1. contract  
2. invariants  
3. authority boundary  
4. epistemic effects  
5. failure modes  
6. acceptance tests  
7. adversarial tests  
8. implement  
9. runtime proof  
10. update maturity matrix  

Forbidden: mark PRODUCTION_PROVEN without evidence; invent evidence; weaken fail-closed; unrestricted capabilities; bypass Tool Gateway; self-promote adaptive change; mix observations/beliefs; treat model confidence as verification; treat recursive hierarchy as proven optimal.

---

## 97. Migration

No greenfield rewrite. Pattern:

```text
current → compatibility adapter → new contract → dual verification → migrate → remove old path
```

Especially: Authority, Event Ledger, Task state, Tool Gateway, OrganizationCompiler.

---

## 98–100. Milestones (renamed)

### M1 — Reality Contact

OTLP collector · real model · Docker isolation CI · remaining survival (malicious/corrupted/human rejection/contradictory) · 48h run.  
(Provider outage / model swap already RUNTIME_INJECTED in harness — keep extending.)

### M2 — Cognitive Organization (experiment)

single → manager-workers → 2-level → 3-level → adaptive compiler; each with baseline.  
**Hypothesis, not axiom.**

### M3 — Recursive Adaptation

Improve organization/environment/retrieval/procedures/routing/verification under promotion gates; still no self-modify of T0 kernel.

---

## Final definition

$$
GlobalOS \neq ManyAgents
$$

$$
GlobalOS = GovernedAutonomousCognition
$$

Stable objects: Goal + EpistemicState + Authority + Environment + Organization + Verification + Effects + Adaptation.

This document is the **Architecture V2 baseline**. Further work must implement and falsify these contracts and hypotheses — not invent a new architecture each cycle.
