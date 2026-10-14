# PREPROD_RELEASE_GATE — v0.1.0-pre (does not weaken RELEASE_GATE.md)

Marks are evidence-backed for development closure. **Human acceptance still required.**
Do not treat this table as `PREPRODUCTION_ACCEPTED` or `PRODUCTION_READY`.

| # | Criterion | Dev evidence | Status |
|---|-----------|--------------|--------|
| 1 | Installs from clean env per OPERATOR.md | `pip install -e '.[dev]'`; PYTHONPATH=src CLI path documented | ☐ human |
| 2 | Real Goal Contract starts end-to-end mission | `gos mission start --goal …`; reactive + live paths | ☑ code+run / ☐ human |
| 3 | status / pause / resume / cancel + resource limits | e2e + CLI; budget gate before tools | ☑ automated / ☐ human |
| 4 | Forced crash + resume | `scripts/preprod_real_kill_recovery.py` SIGKILL + resume SUCCEEDED | ☑ real process / ☐ human |
| 5 | No silent replay of external effects | durable gate; kill recovery `repo.audit=1` | ☑ automated |
| 6 | Software mission delivered + independently checked | SE sandbox reactive+live deliveries under `final_acceptance/missions*` | ☑ runs / ☐ human |
| 7 | Second mission of another type | Research scan mission (reactive+live) | ☑ runs / ☐ human |
| 8 | No false SUCCESS past Completion Gate | negative e2e suite (tool fail, deny, corrupt, budget, bad args) | ☑ automated |
| 9 | Results + spend in audit trail | delivery.json budget/model_cost/model_cycles/receipts | ☑ automated |
| 10 | No open P0 in PREPROD_SUPERVISED | Fork B produce-before-Authority fixed; Gateway-only produce | ☑ claimed for profile / ☐ human |

**Challenge-GA:** NOT_STARTED (separate authorize).  
**v0.1.0-pre RC:** development evidence ready for independent human acceptance — not self-accepted.
