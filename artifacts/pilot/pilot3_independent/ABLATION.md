# Ablation — Arm B (discipline without full Global OS)

**Protocol:** `PILOT3-IND-ENG-v1`  
**Arm id:** `B` (renamed from earlier draft “Arm C”)  
**Purpose:** answer whether incremental value is Global OS infrastructure or
portable engineering discipline.

**Decisive comparison:** **C (GOS) vs B (this arm)** — not only C vs A.

## Arm B stack (allowed)

```text
strong single agent (same model family as A/C)
+ sealed engineering checklist (below)
+ structured finding ledger (JSON schema provided at lock)
+ mandatory local repro (pytest or script) before a finding counts
+ mandatory negative-result retention field
+ same tool allowlist / budget / SHA as A and C
```

## Arm B stack (forbidden — full GOS surfaces)

```text
Authority Kernel / Tool Gateway production path
Epistemic Kernel claim invalidation runtime
OrgCompiler / DCO topology scheduling
Durable runner / Temporal
EnvironmentCompiler
AdaptiveLearning self-modification
Any Global-OS import or in-process harness beyond the sealed checklist docs
```

Arm B may **read** the sealed checklist markdown as input documents.
It must **not** execute Global-OS as the control plane.

## Sealed checklist (binding text at lock)

1. State goal and non-goals before searching.
2. Every finding: path + trigger + observed + expected + severity.
3. Reproduce with minimal command/script before claiming.
4. Keep REJECTED / NOT_REPRODUCED rows; do not delete.
5. Propose fixes only with failing→passing regression test plan.
6. Do not count style-only or speculative CVE without PoC.
7. Separate “claim about readiness” from “defect found.”
8. Stop at budget; do not silently extend.

## Interpretation

| Pattern | Meaning |
|---------|---------|
| C ≫ B on EPI/ENG | Full GOS adds incremental value beyond checklist |
| B ≈ C | Process discipline explains the win; simplify product |
| C ≫ A but C ≯ B | Discipline suffices; do not over-claim architecture |
| B ≫ C | GOS overhead harming; investigate |
| A ≈ B ≈ C | No measured advantage of either discipline or GOS |

## Honesty

Ablation is **not** a strawman. If B wins or ties C, that is a successful
scientific outcome for product focus — not a failure to hide.
