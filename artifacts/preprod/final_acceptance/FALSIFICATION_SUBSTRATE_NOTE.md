# Falsification + Substrate (RC hardening note)

Follow-on to PR #49 RC pack. **Not** a new Kernel.

- Code: `src/global_os/verification/falsifiers.py`, `substrate_health.py`; wired in Completion Gate + `_achiever_settle_step`
- Evidence: `artifacts/preprod/falsification_substrate/COMPARISON.md`
- Tests: `tests/test_falsification_substrate_gate.py`
- Honesty: Cross-Model Critic deferred; no arXiv metric claims

Does **not** self-label `PREPRODUCTION_ACCEPTED`.
