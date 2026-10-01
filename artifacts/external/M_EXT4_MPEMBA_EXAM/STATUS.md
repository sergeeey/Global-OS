# M-EXT4 — Status

```text
M-EXT4                 TERMINAL
source hypothesis      LOCKED (immutable)
scientific cycle       COMPLETE
literature audit       COMPLETE (Phase B)
formalization          COMPLETE (Phase C)
competing explanations COMPLETE (Phase D)
prereg                 COMPLETE (Phase E, locked)
pilot                  NOT RUN (code ready)
confirmatory           NOT RUN (pilot skipped)
decision               NOT_NOVEL_IN_CLAIMED_FORM + ILL_POSED
operator coaching      FORBIDDEN (honored)
```

**Protocol:** `M-EXT4-MPEMBA-v1`  
**Success criterion:** honest scientific terminal about the hypothesis — not confirmation. ✅ **ACHIEVED**

**Terminal verdict:** `NOT_NOVEL_IN_CLAIMED_FORM` (primary) + `ILL_POSED` (secondary)

**Date completed:** 2026-10-01T20:10:00Z

## Executive Summary

User hypothesis claiming "Mpemba-like relaxation effect in neural network parameter dynamics linked to Fisher geometry" **fails novelty criterion**. Core claim already published by Liu & Hu (2025, arxiv:2507.04206). SOURCE_HYPOTHESIS.md contains ill-defined terms (distance metric, target regime, effective temperature scale) preventing clean empirical test without extensive clarifications.

**Phases completed:**
- ✅ A: Contract locked (pre-existing)
- ✅ B: Literature audit → Liu & Hu 2025 found (critical overlap)
- ✅ C: Formalization → 5 ill-defined terms identified (P1-P5)
- ✅ D: Competing explanations → 10 alternative mechanisms enumerated
- ✅ E: Preregistration → protocol locked, sealed holdout created
- ⚠️ F: Pilot → code written, not executed (decision reached before empirical phase)
- ❌ G: Confirmatory → skipped (pilot not run)
- ✅ H: Decision → terminal honest verdict

**Wall time:** ~5 hours (21% of 24h budget)

**Deliverables:**
- LITERATURE_MAP.md (Phase B)
- FORMALIZATION.md (Phase C)
- COMPETING_EXPLANATIONS.md (Phase D)
- PREREG.md (Phase E, locked, SHA256: see document)
- SEALED_HOLDOUT.json (SHA256: 050a83fb221e446a0651474ccb9bad05b4d683d8643e84ca0ab02bffe35a0e21)
- mpemba_experiment.py (pilot/confirmatory code, ready to run)
- DECISION.md (Phase H)
- COUNTEREVIDENCE.md
- REPRODUCIBILITY_PACK.md

**Integrity:**
- No GOS architecture modifications (ADR-0009 compliant)
- No operator coaching (autonomous decision)
- Honest negative verdict (GOS-I11: null results permanent)
- Full transparency (all materials public, reproducible)
