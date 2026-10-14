# PREPROD_RELEASE_GATE — v0.1.0-pre (does not weaken RELEASE_GATE.md)

Marks are evidence-backed for development closure. **Human acceptance still required.**
Do not treat this table as `PREPRODUCTION_ACCEPTED` or `PRODUCTION_READY`.

| # | Criterion | Dev evidence | Status |
|---|-----------|--------------|--------|
| 1 | Installs from clean env per OPERATOR.md | Wheel ships schemas+migrations+cedar; agent mission from `--target` install (`CLEAN_INSTALL_MISSION.json`); editable path still documented | ☑ agent wheel / ☐ human |
| 2 | Real Goal Contract starts end-to-end mission | `gos mission start --goal …`; reactive + live paths | ☑ code+run / ☐ human |
| 3 | status / pause / resume / cancel + resource limits | e2e + CLI; budget gate before tools | ☑ automated / ☐ human |
| 4 | Forced crash + resume | brief_select SIGKILL + **crash-window after write** (`CRASH_WINDOW_RECOVERY.json`) | ☑ real process / ☐ human |
| 5 | No silent replay of external effects | durable gate; write mtime unchanged; write_calls=1 after resume | ☑ automated |
| 6 | Software mission delivered + independently checked | Goal-specific path bind; historical live SE post-hoc **rejected**; nonce Goal oracle | ☑ runs / ☐ human |
| 7 | Second mission of another type | Research scan mission (reactive+live) — smoke, not peer science | ☑ runs / ☐ human |
| 8 | No false SUCCESS past Completion Gate | + wrong write filename ⇒ not SUCCEEDED | ☑ automated |
| 9 | Results + spend in audit trail | tokens/latency measured; `model_cost_forced` honesty for Groq $0 | ☑ automated |
| 10 | No open P0 in PREPROD_SUPERVISED | false-positive write SUCCESS closed in code; human still confirms | ☑ claimed for profile / ☐ human |

**Challenge-GA:** NOT_STARTED (separate authorize).  
**v0.1.0-pre RC:** development evidence ready for independent human acceptance — not self-accepted.
