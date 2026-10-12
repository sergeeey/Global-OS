# Cognitive organs — backlog (contracts-first)

**Status:** `BACKLOG` (not implemented by this doc)  
**Zone:** T2 cognition / eval missions — **not** new T0 Authority surfaces (ADR-0009)

These are the Intelligence/Execution organs the Autonomous Goal Achiever still lacks
as first-class, tested capabilities. Reliability organs (G1–Gfull) are substrate.

## 1. Strategic Goal Decomposer

**Job:** high-level Goal Contract → phased strategy + prioritized subgoal DAG  
**Must:**
- infer domain quality criteria when underspecified (with clarification policy)
- emit phases (e.g. audit → repro → fix → optimize → acceptance) as versioned objects
- prioritize by risk × value; never silently mutate parent Goal (GOS-I06/I27)

**Existing seeds:** `cognition/decomposition`, MissionContract, OrgCompiler hints  
**Gap:** general decomposer beyond repo-audit DAG templates; strategy objects with amend protocol

## 2. Adaptive Closed-Loop Execution (Failure-Driven Re-Planning)

**Job:** on failed approach, pivot hypothesis; retain negatives; continue toward goal  
**Must:**
- record null/failed attempts in ledger (GOS-I11)
- propose strategy amendment (not silent goal overwrite)
- bound retries / spawning (no unbounded agent storms)

**Existing seeds:** null_result events, epistemic invalidation, metareasoning budget  
**Gap:** explicit Pivot / Replan contract + eval that scores adaptation quality

## 3. Dynamic Tool & Model Orchestration

**Job:** choose cheap vs heavy model, local vs distributed tools by task context  
**Must:**
- all model calls via `adapters/models/`; all effects via Tool Gateway
- cost as first-class (GOS-I17); no hidden provider lock-in
- routing policy is evidence-gated T2, not LLM boolean security

**Existing seeds:** FairLlmScheduler, provider adapters, EnvironmentCompiler  
**Gap:** sealed orchestration policy + Challenge metrics for routing quality

## Build order (salami)

```text
1. Challenge Goal Contract + metrics (eval)     — CHALLENGE_CONTRACT_DRAFT.md
2. Decomposer acceptance tests (fail closed)   — before rich planner UX
3. Pivot/Replan schema + tests
4. Orchestration policy stub + cost ledger
5. Wire DEFAULT substrate underneath; run Challenge
```

No organ may bypass Authority Kernel or invent PRODUCTION_PROVEN.
