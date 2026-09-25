# Y20 Execution Protocol — A then B then Unseal

**Preregistration boundary SHA:** `278c10d`  
**Protocol:** `Y20-AB-v1`  
**Status:** READY TO RUN · arms not started · sealed GT UNSEEN

After this boundary, **do not** change scorer, budgets, generator, success criteria,
or outcome interpretation to “improve” results.

## Honest status (do not upgrade until COMPARISON_REPORT)

```text
Y19                         CLOSED / evidence packed
Y19 autonomy attribution    bundle-level only
Y20 prereg                  LOCKED @ 278c10d
Arm A                       NOT RUN
Arm B                       NOT RUN
sealed ground truth         UNSEEN
blind scorer                LOCKED
equal caps                  LOCKED
Global OS advantage         NOT PROVEN
cross-domain transfer       NOT PROVEN
continual SI                NOT MEASURED
M1.5                        NOT CLAIMED
```

## Architecture freeze

**Do not improve Global OS architecture before Y20 completes.**  
Next action is the experiment, not a new subsystem.

## Mandatory sequence

```text
278c10d frozen prereg
       ↓
Arm A  (strong agent + ordinary workspace)
       ↓
save immutable artifacts under arms/A/
       ↓
Arm B  (same model + Global OS structure)
       ↓
save immutable artifacts under arms/B/
       ↓
only now: unseal / load sealed pack for scorer
       ↓
blind scorer (science metrics)
       ↓
attach process logs
       ↓
COMPARISON_REPORT.md
       ↓
claim update (narrow: measurable GOS contribution on this task)
```

**Critical:** finish **both** arms before any sealed peek / unblind.  
Do **not** unseal after A and then run B.

## Equal treatment (both arms)

| Dimension | Rule |
|-----------|------|
| Model + settings | Identical pin recorded at start of each arm |
| Time / tokens / tool calls / compute | Identical caps from `Y20-PREREG.md` |
| Data | Identical `artifacts/y20/public/` (locked sha256) |
| Right to write code | Full for both |
| Operator help | Identical policy: no next-hypothesis dispatch; no sealed hints |
| Arm A | Strong Codex/Claude + ordinary workspace — **not** artificially weakened |
| Arm B | Same model + Goal Contract / durable research state / falsification / stop |

## Process log (required per arm)

File: `artifacts/y20/arms/<A|B>/process_log.json` — see schema in
`process_log.schema.json`. Must record:

```text
human_interventions
dispatcher_asks
hypotheses_tried
failed_experiments
unsupported_claims
tool_calls / tokens / wall_seconds
recovery_events
state_loss_events
premature_stop
evidence_trace_completeness
```

Scientific score alone is insufficient. Equal science + fewer human interventions /
better evidence is a valid architectural win. Equal science + higher cost for B is
also a valid (negative ROI) result.

## After COMPARISON_REPORT — ask precisely

> On this new task, under these equal resources, what measurable contribution did
> Global OS architecture provide relative to the strong-agent baseline?

Not: “Did Global OS win in general?”

## Forbidden until report

- Mutating `y20_causal_ab` scorer / generator / budgets after arm start
- Unsealing before both arm artifacts are immutable
- Claiming GOS advantage / transfer / Continual SI / M1.5
- Reopening Y19 H8
- Improving architecture “to help Arm B”
