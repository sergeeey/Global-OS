# OBSERVATION-SELECTION-1 REPORT

## Verdict

```text
PASS
```

The deterministic selector removes the baseline false SUCCESS on an empty
directory and preserves valid non-empty audit behavior. No LLM, planner,
cascade, memory or new framework was added.

## Base and arms

```text
base/A: 6b312ab21770a18b82f3c1b89f72a61363e9317d (unmodified archive)
B:      C:\gos_obs_sel_1, branch exp/observation-selection-1
```

A is the untouched 6b312ab runtime. B adds only:

- a read-only `repo.inventory` observation;
- a preflight rule:
  - missing target -> invalid, no audit;
  - empty directory -> audit not applicable, no audit;
  - non-empty -> inventory observation then the existing audit pipeline.

No oracle labels are passed to the selector; it sees only the target filesystem.

## Frozen targets

```text
missing   missing path
empty     empty directory
nonempty  directory with README.md + app.py
```

Oracle was frozen in `manifest.json` before the run.

## Results (3 paired repetitions)

| Arm | missing | empty | nonempty | false SUCCESS tasks |
|---|---|---|---|---|
| A baseline | correct rejection | **false SUCCESS** | achieved | **1** |
| B selector | correct rejection | correct rejection | achieved | **0** |

Cost:

| Target | A calls/steps | B calls/steps |
|---|---|---|
| missing | 0 / 3 | 1 / 1 |
| empty | 1 / 3 | 1 / 1 |
| nonempty | 1 / 3 | 2 / 4 |

B non-empty wall time was not worse in this small sample; it added one
inventory call and one observation step.

## Regression

```text
targeted selected tests: 37 passed
full suite: 476 passed, 9 failed, 14 skipped
```

The 9 failures are the same pre-existing frozen-pack/Rust failures as the
6b312ab base (472 passed, 9 failed). No new failures.

## Hidden-oracle / refusal check

- Selector receives only `target_path`; no task ID, oracle or result label.
- It cannot reject everything: the non-empty target must produce a valid audit
  and does so.
- Empty/missing rejection is based on observable inventory state.
- Baseline is unchanged; the selector patch is isolated in B.

## Reproducer

```powershell
$env:PYTHONPATH = "C:\gos_obs_sel_1\src;C:\gos_obs_sel_1"
python C:\gos_observation_selection_1\run_experiment.py
```

Raw data:

```text
artifacts/observation_selection_1/raw_results.json
artifacts/observation_selection_1/manifest.json
artifacts/observation_selection_1/run.log
artifacts/observation_selection_1/FULL.log
artifacts/observation_selection_1/DIFF.diff
```

## Decision

PASS. Keep the minimal selector patch as a candidate for independent review.
Do not expand architecture; no planner/cascade is justified by this experiment.

Residual: only three target classes; no model-driven planning, no failure
recovery beyond preflight, no external effects.
