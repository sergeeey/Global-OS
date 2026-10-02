# M-EXT5 — Mission Brief (agent-facing)

**Status:** `MISSION_OPEN`  
**Protocol:** `M-EXT5-INIT-MPEMBA-v1`

## Assignment

**M-EXT5 — Initialization-induced Mpemba effect**

External scientific mission. Goal is not to prove Global OS useful and not to
rescue M-EXT4. Goal is to settle two questions with unknown outcomes.

### Research questions

1. **H_EFFECT:** At fixed subsequent SGD/data/noise dynamics, can initialization
   alone produce reproducible Mpemba-like crossing (farther at t=0, earlier to target)?
2. **H_FISHER:** If crossing exists, does Fisher/information geometry explain it,
   or do simpler mechanisms?

Treat these as **separate** hypotheses with separate terminals.

### Required process

1. Read M-EXT4 `POST_HOC_AUDIT.md` + `ERRATA.md` (context only; do not “fix” M-EXT4).  
2. Pass **mechanical correctness gate** (`MECHANICAL_GATE.md`) — all items PASS.  
3. Choose and justify **primary endpoint for H_EFFECT** before any confirmatory data
   (crossing definition; distance/target operationalization; do not assume KL(θ,θ*)
   is well-defined without argument).  
4. Put Fisher-related quantities as **mechanistic secondary endpoints** for H_FISHER,
   not as the definition of the effect.  
5. Exploratory **pilot** on separate seeds (engineering reconnaissance only).  
6. If protocol changes after pilot → **new final prereg** then seal.  
7. Freeze code SHA, seal holdout, paired seeds, identical batches/LR/noise.  
8. Confirmatory run + counterevidence + independent verification path.  
9. Dual terminal: H_EFFECT and H_FISHER each get one allowed outcome.

### Deliverables

- `MECHANICAL_GATE.md` (evidence of PASS)  
- `FORMALIZATION.md` / endpoint justification  
- `COMPETING_EXPLANATIONS.md`  
- `PREREG.md` (+ json)  
- `SEALED_HOLDOUT.json`  
- reproducible code + environment pin  
- pilot report (non-confirmatory)  
- confirmatory raw results  
- `COUNTEREVIDENCE.md`  
- `DECISION.md` (dual)  
- `REPRODUCIBILITY_PACK.md`  
- `BOTTLENECKS.md`

### Autonomy

Work autonomously to dual terminal if resources allow. Exact resource blocker only.
Do not ask for content coaching. Do not confirm hypotheses in advance.

### Forbidden

- Editing M-EXT4 immutable artifacts  
- Citing Y24/Y25/M-EXT1–3 as Mpemba evidence  
- Silent easier experiment without amendment  
- LLM-as-numerical-oracle for results  
