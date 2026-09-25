# Y19 Evidence Pack

**Purpose:** Keep Y19 reproducible evidence, not a story.  
**Science status:** FROZEN · milestone SHA **`4378005`**  
**Do not reopen** in-family Hx / feature-mining.

## Milestone & contracts

| Item | Location |
|------|----------|
| Milestone commit | `4378005` |
| Program contract | `artifacts/y19/Y19-RESEARCH-PROGRAM.md` |
| Split claims | `artifacts/y19/CLAIMS.md` |
| Durable halt state | `artifacts/y19/CURRENT_STATE.json` |
| Eval harness | `src/global_os/evals/research/y19_transient_early_warning.py` |
| Tests | `tests/test_y19_transient_early_warning.py` |

## Per-hypothesis artifacts

| Step | Decision | Artifact dir |
|------|----------|--------------|
| H1 | REJECTED | `artifacts/y19/Y19-H1-transient-early-warning/` |
| H2 | SUPPORTED | `artifacts/y19/Y19-H2-baseline-mechanism/` |
| H3 | SUPPORTED | `artifacts/y19/Y19-H3-h2-robustness/` |
| H4 | REJECTED | `artifacts/y19/Y19-H4-size-entropy-decomp/` |
| H5 | SUPPORTED (H5b) | `artifacts/y19/Y19-H5-why-n/` |
| H6 | SUPPORTED (H6b) | `artifacts/y19/Y19-H6-structural-ablation/` |
| H7 | SUPPORTED (H7a) | `artifacts/y19/Y19-H7-period-loo-transfer/` |

Each dir holds TZ / preregistration / mission / claims / verification / run_manifest /
experiments/metrics (immutable decision payloads for H1–H4 must not be rewritten).

## Seed policy (harness constants)

Locked in `y19_transient_early_warning.py` (disjoint ranges per Hx). Representative:

- H1: train `1000–1179`, hold `5000–5119`
- Later Hx use dedicated TRAIN/HOLD blocks documented in each protocol version string
  (`Y19-H2-v1` … `Y19-H7-v1`).

## Who chose the next step (H5→H7)

| Question | Record |
|----------|--------|
| Operator asked to pick H5/H6/H7? | **No** |
| Human interventions between H5–H7 for next-hypothesis choice | **None** |
| Next step selected by | Y19 program + agent from evidence / EVI (campaign contract) |
| Stop reason | `terminal_scientific_result` |

## Attribution note

Evidence supports Claim B as **bundle autonomy** (model + GOS + infra), not
architecture-only superiority. Architecture contribution is deferred to Y20 A/B.

## Forbidden without new program

- H8 in-family feature hunt
- Relabeling as Continual SI / M1.5 / production autonomy
- Mutating sealed holdout criteria post-hoc
