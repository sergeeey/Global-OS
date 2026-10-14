# Goal Engineering — Systematic Source Review

**Protocol:** GE-STUDY-v1  
**Review date:** 2026-10-14  
**Inventory:** `sources.json`  
**Stance:** Advantages of Goal Engineering are **not** assumed. Human goal-setting evidence and agent-harness evidence are priors, not proof of GE for LLM agents.

## 1. Scope

Question: Does tasking autonomous AI agents with **verifiable goals** (Definition of Done + EvidenceLedger) improve quality, reliability, and effectiveness versus (a) traditional vague prompts and (b) detailed procedural instructions?

Included: peer-reviewed agent benchmarks, goal-setting meta-analyses, verification/false-positive studies, harness A/B preprints, engineering closure-contract artifacts.  
Excluded: marketing claims without metrics; self-reported agent “success” without oracle.

## 2. Classical goal-setting (transfer prior only)

Locke & Latham (2002, 2019) and Wood et al. (1987):

| Finding | Implication for agents |
|--------|-------------------------|
| Specific + difficult goals > “do your best” (d ≈ 0.42–0.80) | Vague prompts under-specify acceptable outcomes |
| Feedback is a moderator; goals+feedback > either alone | DoD without runtime evidence checks is incomplete |
| Effects shrink on complex/novel tasks unless strategy/learning goals exist | Multi-step autonomy may need process criteria, not only outcome slogans |
| Specificity reduces variance when performance is controllable | Machine-checkable criteria reduce idiosyncratic “done” |

**Transfer limit:** These studies are about humans. They justify hypotheses, not agent conclusions.

## 3. Agent benchmarks: success is hard; validators matter

- **AgentBench (ICLR 2024):** interactive agent success varies widely; static QA ≠ agency.
- **WebArena (ICLR 2024):** best GPT-4 agent ~14.4% end-to-end vs ~78% human; functional validators used.
- **GAIA (ICLR 2024):** exact-match gates; hard levels near zero for strong models vs ~92% human.

Implication: evaluation must be outcome/oracle based; agent self-report is insufficient.

## 4. Weak verification inflates “success”

- SWE-bench re-validation: ~7.8% plausible patches fail fuller developer tests; resolution inflated ~4.5pp (up to ~6.4pp in sensitivity analyses).
- SWE-ABS: ~19.8% of leaderboard-accepted patches rejected under strengthened suites; top agent −16.6pp.

Implication: **EvidenceLedger quality** (scope-matched, latest-state, adversarial-strength checks) is load-bearing. A weak DoD can create false confidence — the opposite of Goal Engineering’s intent.

## 5. Harness components: planning vs verification

*How Do Agent Harnesses Create Value?* (arXiv:2609.20474):

- Fixed task-specific plans beat length-matched sham guidance by **+7.17pp** oracle success (90% CI 1.15–13.36), gains on complex tasks.
- Read-only terminal verifier rejects **61%** of oracle-invalid episodes, withholds **17%** of correct ones, cheaply.
- Under high cost of erroneous acceptance, verifier value dominates planning; under low liability, planning gain dominates.

Implication: GE (outcome criteria + evidence gate) is closer to the **verifier / release-control** lever than to “more prose in the prompt.” Detailed instructions resemble the **planning** lever — useful, especially when complete and world-stable; brittle when incomplete or when the world drifts.

## 6. Engineering practice (design priors)

Goal-to-Proof, Hermes completion contracts, GoalBuddy receipts converge on:

1. State the observable result before acting.  
2. Bind completion to executed checks / receipts.  
3. Fail closed on missing evidence.  
4. Keep authority with the user for irreversible acts.

These are **not** RCTs. They define the GE construct operationally.

## 7. Synthesis (pre-experiment)

| Claim from literature | Status |
|----------------------|--------|
| Vague prompts underperform specific goals (humans) | Strong in humans; **unproven** for agents until measured |
| Detailed plans can raise success vs sham | Supported in one harness study |
| Verifiers cut false passes | Supported; trade false negatives |
| Test-based “done” can still be wrong | Strongly supported (SWE-bench line) |
| GE (DoD+Ledger) dominates both baselines always | **Not established** — needs controlled comparison |

## 8. Gap this study fills

No located source runs a locked three-arm comparison **S_TRAD vs S_DETAIL vs S_GE** on coding + research + multi-step with oracle success, autonomy, cost, latency, and evidence fidelity under an independent evaluator. GE-STUDY-v1 provides that protocol and a **deterministic behavioral** execution class; live-LLM execution remains separate (see PROTOCOL / RESULTS).
