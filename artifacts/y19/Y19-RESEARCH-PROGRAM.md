# Y19 Research Program — Autonomous Campaign Contract

**Status:** Binding for Y19 scientific dogfood  
**Not:** M1.5 exam · Long-Horizon 96m/48h · Continual SI claim  

## Terminal mission

Autonomously determine which mechanisms allow prediction of **long transients** in the
studied NK Boolean family; separate real predictors from proxies and artifacts; test
transfer to unseen regimes; drive the branch to the **narrowest reproducible claim**
the evidence supports (`SUPPORTED` / `REJECTED` / `INCONCLUSIVE` equally valid).

H1, H2, H3, … are **internal steps**, not operator tickets.

## Operating loop

```text
current evidence
  → competing explanations
  → discriminating experiment (preregistered)
  → falsification / holdout
  → result
  → update durable state
  → next highest-EVI question
  → …
```

**Closed hypothesis = checkpoint, not end of mission.**

## Autonomy rules

1. After each closed H, **do not** ask the operator to pick the next hypothesis,
   method, or experiment if the choice is decidable from evidence + this contract.
2. Choose the next step by **expected information value** under active open hypotheses.
3. Preserve sealed holdouts; never adapt hypothesis or criteria after holdout peek.
4. On Global OS defect: failure case → minimal fix → regression → replay → **resume
   the same scientific mission**. Do not invent a new T0/T1 subsystem from one failure
   (see `artifacts/hardening/DEVELOPMENT_RULES_DOGFOOD.md`).
5. After each finished research step: update handoff files → `git commit` checkpoint →
   **continue**. Do not treat the chat reply as mission completion.
6. Read this file + `CURRENT_STATE.json` at session start **before** any clarifying
   question. If `stop_reason` is null and the terminal goal is unmet, execute
   `NEXT_BEST_ACTION.md`.

## Hard forbids (need explicit operator permission)

- Windows 96m wall preflight
- Literal 48h / `GOS_START_RESEARCH_48H`
- Claiming M1.5, H-ORG, Continual SI, PRODUCTION_PROVEN
- Fabricating live provider IV / mutating `Y18-4-FC-IV` to PASS

## Stop conditions (only these)

Stop and write a full handoff when **any** holds:

1. **Terminal scientific result** — narrow reproducible claim achieved for the mission.
2. **Low EVI** — further experiments in-family add little discriminating power.
3. **Real blocker** — cannot proceed in this environment (missing capability/data).
4. **Operator authority needed** — secret, approval, or policy outside agent scope.
5. **Critical integrity defect** — subsequent results would be untrustworthy until fixed.

## Handoff packet (required on stop OR session end)

| File | Purpose |
|------|---------|
| `CURRENT_STATE.json` | phase, closed Hx, active question, `stop_reason` or null |
| `WHAT_WE_KNOW.md` | narrow claims only |
| `WHAT_FAILED.md` | rejected paths + nulls |
| `OPEN_HYPOTHESES.md` | remaining competing explanations |
| `NEXT_BEST_ACTION.md` | concrete discriminating experiment for resume |

A new session must be able to continue **without human dispatch**.

## Intellectual autonomy ≠ infinite physical process

One cloud session may die. Durable state + this contract make the **next** session
resume the same terminal goal. That resume path is part of the Global OS dogfood.

## Evidence so far (bootstrap)

| Step | Decision | Narrow reading |
|------|----------|----------------|
| H1 | REJECTED | spectral/sensitivity extras fail MCID vs baseline |
| H2 | SUPPORTED | size/entropy beat activity-only |
| H3 | SUPPORTED | H2 survives activity-match, unseen-N, K regimes |
| H4 | REJECTED | entropy dies under N control → effect mostly **N** |

Natural next EVI step: **why N?** (state-space vs basin/cycle structure vs proxy vs protocol artifact).
