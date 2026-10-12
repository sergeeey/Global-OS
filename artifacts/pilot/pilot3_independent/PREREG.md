# PREREG — PILOT3-IND-ENG-v1

**Status:** `PREREG_DRAFT`  
**Protocol id:** `PILOT3-IND-ENG-v1`  
**Primary hypotheses:** `H-PILOT3-EPI`, `H-PILOT3-ENG`, `H-PILOT3-EFF`  
**Attribution:** `H-PILOT3-ATTR` (see `ABLATION.md`) — **key comparison C vs B**

## Why this pilot exists

Pilot 2 fidelity was `SAME_EXECUTOR_DUAL_PROTOCOL`. One executor running two
protocols can transfer knowledge across arms. Therefore Pilot 2 supports
**process advantage** only — not independent proof of architecture superiority.

Pilot 3 upgrades fidelity to independent validation + disciplined ablation (Arm B).

## Lock sequence

```text
1. Choose target repo + pin SHA (prefer fresh pin ≠ Pilot 2 contaminated tip)
2. Seal rubrics (this file + FINDING_RUBRIC + METRICS + ABLATION)
3. Assign distinct executors/sessions for A, B, C, D (record ids in LOCK.json)
4. Seal provider/model/tool/budget pins
5. Run A, B, C in isolation (order randomized; no shared scratch)
6. Blind eval by D on anonymized finding packs
7. Unseal scores → DECISION.md
```

Amendments after lock require `PREREG_AMENDMENT.md` **before** score unseal.

## Fidelity requirements (hard)

| Requirement | Rule |
|-------------|------|
| Separate executors | Distinct cloud-agent run ids **or** hard-isolated sessions with no shared context |
| Same SHA | All arms clone identical commit |
| Same information set | Shared task brief only; no arm sees another's findings |
| Pre-registered budget | Wall + token/API caps sealed; overrun → arm `BUDGET_EXCEEDED` |
| Blind evaluation | Evaluator D sees anonymized packs (labels shuffled); no chat memory from A/B/C |
| No self-certification | Arm author ≠ scorer for that arm's primary metrics |

Violation of any row → that comparison is `INCONCLUSIVE` for architecture claims.

## Provider / budget pins (fill at lock)

| Pin | Value | Notes |
|-----|-------|-------|
| Model family | _TBD_ | same for A/B/C |
| Provider | _TBD_ | preferably distinct run instances |
| Tool set | _TBD_ | same allowlist |
| Wall budget | _TBD_ | e.g. 4h each |
| Token/API budget | _TBD_ | comparable hard cap |
| Network policy | clone once; offline pytest thereafter | same |
| Human help | scripted interventions only; counted toward EFF |

## Ordered evaluation (per hypothesis)

Do **not** collapse to a single magic number.

### H-PILOT3-EPI (epistemic quality) — C vs A

```text
1. No critical invariant / safety regression in proposed fixes
2. Lower unsupported_claim_rate (C vs A)
3. Lower false_positive_finding_rate (C vs A)
4. Negative results retained (no silent drop)
```

### H-PILOT3-ENG (engineering value) — C vs A

```text
1. Gate (1) from EPI
2. More confirmed material findings (severity-weighted)
3. More correct regression-safe fixes (failing→passing tests)
4. Independent repro rate by D ≥ sealed threshold
```

### H-PILOT3-EFF (effort) — C vs A

```text
1. Quality floor: ENG quality not worse than A beyond sealed tolerance
2. Lower human_review_minutes for comparable confirmed set
3. Lower intervention_count
4. Cost reported; not sole win criterion
```

### H-PILOT3-ATTR (decisive) — C vs B

```text
If B ≥ C − tolerance on EPI and ENG and EFF,
  → ATTR = PROCESS_DISCIPLINE_SUFFICES (GOS incremental NOT_SHOWN)
If C > B on ≥2 of {EPI, ENG, EFF} with sealed deltas and comparable cost,
  → ATTR = GOS_INCREMENTAL_SUPPORTED (under this fidelity)
If C > A but C ≯ B,
  → ATTR = PROCESS_DISCIPLINE_SUFFICES (do not claim architecture win)
Else → ATTR = INCONCLUSIVE
```

## Terminal vocabulary

| Verdict | Meaning |
|---------|---------|
| `SUPPORTED` | Hypothesis holds under ordered eval + fidelity |
| `REJECTED` | Opposing arm dominates on primary ordered criteria |
| `TIE_WITHIN_TOLERANCE` | No clear advantage |
| `NOT_SHOWN` | Advantage claim not justified (incl. ATTR) |
| `INCONCLUSIVE` | Fidelity break, budget incomparability, or target unsound |

## Forbidden after lock

```text
change primary metrics
weaken A or B tools/docs to flatter C
give C extra secrets or private context about the target
retune OrgCompiler mid-run for score
discard negative findings
unblind evaluator D before score seal
same-agent self-certification of primary scores
```

## Target selection guidance

Prefer an engineering repo **not** already fully mined by the same executor on
the same SHA (avoid Pilot 2 contamination). Candidates may include a **new pin**
of mcp-bouncer post-fix, ContextProof, or another stdlib-light security/filter
project — recorded in `LOCK.json` at lock time with rejection reasons.

## Relationship to product thesis

```text
Candidate product = evidence-backed repository auditing
  with reproducible findings + controlled corrections.

Pilot 3 asks: how much of that value needs Global OS runtime (C)
  versus a thin discipline checklist (B)?
```
