# Fidelity — PILOT3-IND-ENG-v1

## Pilot 2 limitation (binding context)

| Field | Pilot 2 |
|-------|---------|
| Fidelity | `SAME_EXECUTOR_DUAL_PROTOCOL` |
| Verdict | `PARTIAL_SUPPORT_PROCESS_ONLY` |
| Intelligence advantage | `NOT_SHOWN` |
| Why insufficient for architecture proof | knowledge transfer across arms by one executor |

## Pilot 3 target fidelity

| Field | Required |
|-------|----------|
| Label | `INDEPENDENT_EXECUTORS_PLUS_ABLATION` |
| Arms | A, B, C isolated |
| Evaluator | E blind, separate |
| Cross-leak | forbidden until after score seal |

## Acceptable executor separation

Any of:

1. Distinct cloud-agent runs with distinct `bcId` / session ids, no shared transcripts.
2. Distinct human-operated sessions with wiped context and sealed brief only.
3. Distinct provider accounts **if** model family pins remain comparable (record in LOCK).

Not acceptable:

```text
same continuous chat switching “now you are Arm A / Arm B”
shared scratchpad / branch with prior arm findings
evaluator who authored an arm under score
```

## Contaminated targets

If the same executor already mined a SHA (e.g. Pilot 2 on mcp-bouncer@45af092),
that SHA is **contaminated for that executor**. Prefer:

- new pin after external fix merge, **or**
- different repository, **or**
- executors with no prior exposure to that audit pack

Contamination → mark comparison `INCONCLUSIVE` for ENG superiority claims
(EPI labeling discipline may still be informative — disclose).
