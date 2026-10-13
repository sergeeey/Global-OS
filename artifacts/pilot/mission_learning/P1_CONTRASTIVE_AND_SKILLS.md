# P1 — Contrastive Failure Miner + Evidence Skills + Transfer Eval

Analyze-only extensions to Mission Learning Loop v0. No runtime auto-mutation.

| Piece | Code | Tests |
|-------|------|-------|
| Contrastive Failure Miner | `evals/mission_learning/contrastive.py` | `tests/test_contrastive_miner.py` |
| Evidence-backed Skill Library | `cognition/skills/evidence_library.py` | `tests/test_evidence_skills.py` |
| Protected Transfer Eval | `evals/mission_learning/transfer_eval.py` | `tests/test_evidence_skills.py` |

## Explicitly rejected from external RSI folklore

- 7/10 trials as universal skill admission
- Chernoff–Koopman as RSI depth controller (no grounded model here)
- LLM Test Agent as sole independence guarantee
- Mandatory MicroVM for RSI (sandbox policy remains Authority/Gateway)

## Promotion

Skills stay `EXPERIMENTAL` until human promotion with **disjoint** transfer evidence
and adequate sample (small n / ~70% rate rejected). Challenge-GA holdout ≠ train.
