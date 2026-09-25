# R1–R3 Recurring Failure Classes

**Compiled:** 2026-09-25  
**Rule:** harden only classes seen in **≥2** independent real missions  
(`DEVELOPMENT_RULES_DOGFOOD.md`).  
**Not:** raw-IQ failure (never claimed) · Y23 reopen.

## Matrix

| ID | Class | Seen in | Severity | Harden now? |
|----|-------|---------|----------|-------------|
| FC-01 | Historical artifact rewrite by tests/executors (provenance noise) | R3 A-F5; live pytest Y18/Y19 regen during R1/R2 sessions | HIGH | **YES** |
| FC-02 | SHA field semantics ambiguity (dir merkle vs file hash) | R3 A-F1; Y21/Y22 process_logs; R2-HDE false alarm | MEDIUM | **YES** (docs+test; no frozen rewrite) |
| FC-03 | Environment/tooling block on “full” upstream stack | R2 official retrain BLOCKED; Y18-4 provider IV often BLOCKED | MEDIUM | Policy only: always record BLOCKED ≠ fail-closed invent |
| FC-04 | Self-certification of usefulness | R1 EVALUATION self-scored; fixed in R2/R3 independent review | MEDIUM | **YES** (process: R4+ must keep independent contour) |
| FC-05 | Degenerate/wrong experiment before fix | R2 untrained probe collapse; R3 false agency-missing hyp | LOW–MED | Process OK (failure→fix worked); no new subsystem |
| FC-06 | Sealed GT local-only (gitignored) | R3 A-F2; Y21/Y22 design | LOW | Docs only (intentional) |
| FC-07 | Expensive richer trace without primary sealed gain | Y20–Y22 | INFO | No harden — map already frozen; do not retune scorers |
| FC-08 | Human dispatcher interventions | R1–R3 all 0 | — | Not a failure |

## Harden decisions

1. **FC-01:** `GOS_MISSION_ARTIFACT_ROOT` + tests run in isolated copies; default refuse silent rewrite of historical trees unless `GOS_ALLOW_HISTORICAL_ARTIFACT_REWRITE=1`.
2. **FC-02:** keep `SHA_BINDING_NOTE.md`; add regression test that Y22 `public_pack_sha256` equals dir merkle of `artifacts/y22/public`.
3. **FC-04:** document binding in `artifacts/hardening/REAL_USE_RULES.md` — independent review required for R-missions.
4. **FC-03/05/06/07:** no new code subsystem.

## Explicit non-recurring (do not subsystem)

- One-off paper env (torch-nightly) for AttentionExplanation  
- NYC 311 sample bursts (sample-relative)

## Next after harden

stable SHA → freeze pin → compressed preflight + Linux os_kill smoke →  
Windows preflight / literal 48h **only on operator Windows** → audit → M1.5 candidate honesty.
