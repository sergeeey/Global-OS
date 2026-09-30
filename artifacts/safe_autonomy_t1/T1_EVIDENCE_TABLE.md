# T1 immutable evidence table

**Status:** IMMUTABLE for T1 identity  
**Do not edit verdict rows after publication; amend only via new experiment IDs.**

| Version | Hypothesis | Evidence | Verdict |
|---------|------------|----------|---------|
| **T1** | thin MA reduces escapes without unacceptable utility tax | deterministic fault pack v1 (`DETERMINISTIC_FAULT_MISSIONS_v1`) | **REJECT** |
| Component supported | escape reduction is large | MIER C=0.0 vs A=0.9 / B=0.8 | supported component |
| REJECT cause | utility/completion gain insufficient vs frozen rules | completion A→C drop > `utility_tax_max`; SSR Δ(C−B)=0.1 ≪ `ssr_win_abs=0.18` | **verifier tax (Verifier Tax 2.0)** |
| Generalization | live LLM / production / other packs | not measured | **UNKNOWN** |
| M1.5 coupling | long-horizon cognitive 48h | separate closed scope | **not reopened by T1** |
| MCID | SET_BY_VARIANCE_PILOT_v1 | frozen before T1; not recomputed from residuals | **unchanged** |

## One-sentence lasting claim

> Thin Mission Assurance in T1 **strongly cuts material escapes** but in this form **pays an unacceptable useful-autonomy / completion tax**; therefore H_TRUST is **REJECTED in tested scope**, not “the mechanism is useless.”

## Pointers

- Decision: `T1_DECISION.md`
- Diagnostics: `POST_T1_DIAGNOSTICS/DIAGNOSTICS.md`
- Revival: `REVIVAL_TRIGGERS.json`
- Future pack: `PACK_V2/` (sealed)
- ADR: `docs/adr/ADR-0011-t1-mission-assurance-reject.md`
