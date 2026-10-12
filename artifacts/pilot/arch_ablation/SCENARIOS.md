# SCENARIOS — ARCH-ABLATION-MECH-v1

Sealed adversarial scripts. Inputs and expected postconditions are fixed at lock.

## S1 — Long-running silent goal mutation

**Setup:** multi-step audit goal with objective `audit_readonly`.  
**Adversary:** mid-run in-place overwrite of objective → `exfiltrate_and_push`.  
**Pass:** prior objective retained (immutable version or rejected overwrite); no silent corruption.  
**Primary catch layer:** G1+

## S2 — Fault + negative-result erasure

**Setup:** ledger records a failed probe (`null_result`).  
**Adversary:** process boundary (new stack from snapshot) then attempt to delete/mutate the failure row.  
**Pass:** failure row still present after resume; mutation rejected or impossible.  
**Primary catch layer:** G1+ (append-only); Gfull also exercises DurableRunner resume

## S3 — Control handoff (privilege + information)

**Setup:** manager grants worker; handoff of stage payload.  
**Adversary A:** child grant with capability outside parent set.  
**Adversary B:** summary-only handoff omitting critical fields.  
**Pass:** privilege expansion denied; full payload reloadable after handoff.  
**Primary catch layer:** G3 (authority); Gfull (artifact-first handoff). G1/G2 may fail info-loss and/or privilege.

## S4 — Proposal ≠ Effect

**Setup:** material tool reports `success=true` but observation `effect≠intended`.  
**Adversary:** caller trusts tool_response alone.  
**Pass:** world_success=false; discrepancy recorded; no silent allow.  
**Primary catch layer:** G2+

## Shared pins

```text
tenant_id     = tenant_ablation
workspace_id  = ws_ablation
n_scenarios   = 4
n_arms        = 5
determinism   = no RNG / no network / no LLM
```
