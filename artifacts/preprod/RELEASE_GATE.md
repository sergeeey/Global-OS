# Pre-production readiness gate (manual)

Marks are **not** auto-checked. Independent acceptance only.

| # | Criterion | Status |
|---|-----------|--------|
| 1 | Deploys from clean env per OPERATOR.md | ☐ |
| 2 | Real Goal Contract starts live end-to-end mission | ☐ (local e2e green; human to confirm) |
| 3 | status / pause / resume / cancel + resource limits | ☐ |
| 4 | Forced crash + resume verified | ☐ (automated in e2e; human to confirm) |
| 5 | No silent replay of external effects | ☐ (idempotency probe in e2e) |
| 6 | One software mission delivered + independently checked | ☐ |
| 7 | Second mission of another type done or honestly limited | ☐ |
| 8 | No false SUCCESS past Completion Gate | ☐ |
| 9 | Results + spend in audit trail | ☐ |
| 10 | No open P0 in allowed launch profile | ☐ |

**v0.1.0-pre** only when all 10 are human-checked. Challenge-GA is separate.
