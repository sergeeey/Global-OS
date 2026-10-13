# T3 A/B measurement defect — model-insensitive escapes

**Status:** `MEASUREMENT_DEFECT_DOCUMENTED`  
**Tip audited:** `2f73107`  
**Boundaries unchanged:** `ATTR=NOT_SHOWN` · `M2=CLOSED` · `PRODUCTION_PROVEN=0`

## Finding

On tip `2f73107`, arms **A** and **B** appended material escapes from `eff_scenario` /
`arm_id` labels, not from `AgentDecision` fields. Substituting worst / best
`propose_action` stubs left MIER/SSR byte-identical (external audit + code review).

Therefore T3 L1 **KEEP numbers for A/B cannot evidence model-dependent safety**.
Harness may still call a live provider; the scored escapes did not use the reply.

## Mitigation (this branch)

- `escape_from_model_decision()` — escapes from claim/evidence/observation fields
- Arms A/B use that helper (authority-expand check on B retained)
- `tests/test_t3_model_sensitivity.py` — worst vs best stubs **must** change escape counts

## Honesty consequence

- Do **not** read historical `T3_DECISION.md` L1 A/B MIER as “live LLM behavior shown”
- Accurate claim: “provider may be invoked; A/B escape scoring was scripted until fix”
- C2: decision-coupled scenario mapping in `t3_arm_runners` (GREEN proposal →
  `benign` route) so router actions change with stubs; **frozen**
  `recovery_router.py` / C2 contract pins untouched (no post-unseal retune)
- No new KEEP/REJECT invented here; no Trust Kernel / PRODUCTION_PROVEN promotion

## Non-claims

```text
≠ T3 overturned into REJECT by this note alone
≠ architecture proven useless
≠ Pilot 2/3 results rewritten
≠ Challenge-GA blocked forever
```
