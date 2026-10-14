# activeContext — Global OS / Goal Engineering
_Last updated: 2026-10-14 (Asia/Almaty) · research branch only_

## Active direction
Apply Goal-Contract Prompting / Goal Engineering to the existing Global OS **Autonomous Goal Achiever** architecture. Study memory, context, planning, tools, authority, verification and historical failures; test new components only as isolated, reproducible T3 experiments. Never claim production readiness from synthetic tests.

## Binding inherited facts and gates
- Global OS Architecture V2 is contract-first; the LLM is replaceable compute. Invariants are binding in `CONSTITUTION.md`; read `SPEC-ADDENDUM-V2.md` and `AGENTS.md` before any change.
- Keep Pilot 3 `PROCESS_DISCIPLINE_SUFFICES` / GOS incremental advantage `NOT_SHOWN`, and M2 org superiority `CLOSED`. Y25 memory advantage was `NOT_SHOWN` at preregistered strength. See `docs/SCIENTIFIC_HONESTY_MAP.md`.
- `ARCH-ABLATION-MECH-v1` is **scripted mechanism** evidence (not LLM superiority). `MINIMAL-STACK-v1` default G1+G2+G3, Gfull opt-in; stop micro-reproving sealed layers.
- ADR-0009: no new T0/T1 surfaces. Challenge-GA `PREREG_LOCKED` / `NOT_STARTED`; **do not execute or retune without explicit authorization**. Do not merge experimental changes automatically.
- Each claim of `VERIFIED` requires method, provenance and independent evidence; `tool success != world effect`; `implemented approximation != fulfilled contract`.

## 2026-10-14 reconnaissance result
- Triage: 25 distinct external papers/docs/repositories checked for relevance and date where available, plus current repository's architecture, honesty map and failure history. This is source reconnaissance, **not 25 full-paper reviews**.
- 12 falsifiable technical hypotheses identified; top three: (A) dependency-closed context capsule, (B) targeted verifier/expiry routing, (C) planner pivot informed by failure taxonomy.
- Source-level observation: `src/global_os/cognition/context/assembler.py` (blob `110b4fe53999478b05712f24e3c1aad71663cb0b`) uses priority sorting with token-budget greedy selection and no local freshness, goal-scope, or dependency-closure validation at selection boundary. Upstream controls may exist; source-level gap is not proof of end-to-end bug.

## Isolated PoC: GCP-CTX-CLOSURE-v1
- Candidate A implemented **outside repo and without production effects** as a local Python T3 proof-of-mechanism. Baseline **reproduces source's selection policy**, not actual Global OS runtime.
- Deterministic comparison: 500 matched synthetic scenarios (5 families × 100 seeds), 6 checks, no LLM. Full declared invariants baseline 4.6% vs PoC 100%; mandatory recall 63.67% vs 100%; **target-claim recall declines 78.25% → 61.58%**. Mean conditional-token use 126.50 vs 123.99.
- Crucial caution: synthetic fixtures deliberately stress guarded conditions; 100% mechanism pass is **not** external validity, novel science, increased real task completion, security proof, or production readiness.
- Verdict **ITERATE**; **do not ADOPT in production**. Proposed next test: independent unseen task-outcome evaluation vs real ContextAssembler under matched budgets and models, with human/authority gate for changes.
- The full local report / script / results are separate downloadable research artifacts; **do not claim they are in this GitHub commit**.

## Next authorized scientific work
1. Extend evaluation to real package integration without changing T0/T1.
2. Lock fresh task-level cases and model/tool budgets; measure false-done, claim recall, verified completion, cost, and abstention.
3. Preserve negative outcomes and prior frozen claims; require approval/ADR before any promotion.

## Decision
`ITERATE` (T3 prototype only). No production auto-promotion, no Challenge-GA execution, no schema/core/authority mutations.
