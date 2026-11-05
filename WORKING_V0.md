# WORKING V0 — supervised read-only repo audit

Status: **LIMITED WORKING V0 CANDIDATE** — not production-proven, not
self-improving.

## What this is

One user command that runs a goal through the independently accepted
`c3074fa` supervised, read-only repo-audit path:

```text
Goal Contract
  -> target observation
  -> accepted repo-audit
  -> verification/evidence
  -> truthful terminal
  -> delivery artifact + human report + trace
```

No planner, memory, learning, diagnostic-generalization, admissibility
framework, write action, external effect or RSI is included.

## Run

From a checkout of this branch/worktree:

```powershell
$env:PYTHONPATH="C:\gos_working_v0\src;C:\gos_working_v0"
python -m global_os.cli --root C:\temp\gos-state mission run `
  --goal "Провести проверяемый read-only аудит репозитория" `
  --target C:\path\to\repository
```

The installed console script uses the same command:

```text
gos --root <state-dir> mission run --goal "<goal>" --target <path>
```

`--root` is mandatory in effect for a read-only mission: the resolved state
root must be outside the resolved `--target`. The CLI rejects the invocation
with exit 2 before creating any state if `--root` is equal to or inside
`--target`, including the default `./.gos` when run from inside the target.

## What the user gets

```text
mission_id
terminal
verdict (SUCCEEDED / FAILED / INCONCLUSIVE / INVALID_TARGET)
reason
report:   <run-dir>\REPORT.md
evidence: <run-dir>\delivery.json
trace:    <run-dir>\events.json
artifact: <run-dir>\artifacts\sha256\<digest>
```

Exit codes:

```text
0  SUCCEEDED
3  INCONCLUSIVE / INVALID_TARGET
4  FAILED
2  CLI/configuration error
```

The terminal comes from the accepted mission delivery/completion records, not
from "the tool returned without an exception".

## What v0 really does

- accepts a goal string and a target path;
- records the mission, events, budget, tool calls and delivery under the
  external `.gos` state root;
- performs a read-only repository audit;
- verifies the report shape (`read_only`, `modified_target`, findings, scan);
- returns `SUCCEEDED` only when the accepted completion gate is achieved;
- returns `INCONCLUSIVE` for empty targets and `INVALID_TARGET` for missing or
  non-directory targets;
- writes a human-readable `REPORT.md`, machine-readable `delivery.json` and the
  audit artifact.

## What v0 does NOT do

- arbitrary goal solving or planning;
- code changes, commits, pushes, deployments or external API effects;
- write actions in the target repository;
- memory, lessons, transfer or learning;
- diagnostic strategy selection, shared admissibility or adaptive recovery;
- long-horizon autonomy, multi-agent cascade or RSI;
- production readiness.

## Known limitations

- the goal contract is a fixed repo-audit contract derived from the CLI text;
- only read-only static repository audit is supported;
- no recovery of a wrapped repository in this v0 (the accepted `c3074` line
  does not include the unaccepted `901a` recovery candidate);
- no independent production acceptance; the accepted scope is the narrow
  `c3074` observation/terminal path;
- no user UI beyond CLI text and files;
- `.gos` is local state, not a production store.

## Provenance

```text
accepted base: c3074fac93e8159fefc2e9944b53902c31236709
candidate:     feat/working-v0-accepted (exact SHA in final acceptance record)
branch:        feat/working-v0-accepted
```

`main` is not modified by this candidate. The local `main` is dirty, 49 commits
behind `origin/main`, and does not contain the accepted preprod line; merging it
would import unrelated history. This branch starts from the accepted
`c3074fa` line and adds only the CLI/report surface and tests.

## Production / learning

```text
PRODUCTION_PROVEN: NO
LEARNING:          NOT PROVEN
SELF-IMPROVEMENT:  NOT PROVEN
```

This is a limited working candidate for real supervised repo-audit use, not a
general autonomous runtime.
