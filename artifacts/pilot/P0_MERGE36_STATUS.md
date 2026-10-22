# P0 — Coherent main (updated)

> **HISTORICAL:** #37 **MERGED** (`232022c` stack). Current tip: `docs/Project.md` / `RUN_STATE.json`.

**Status:** MERGED via [#37](https://github.com/sergeeey/Global-OS/pull/37) (see `P0_MERGE37_REQUEST.md`)  
**#36:** closed as superseded by #37 (same stack + MLLv0)  
**#32–#35:** closed as superseded  
**`main` tip at write time:** `2f73107` — merge of #37 was then required (done 2026-10-13)  
**Dogfood:** no autonomous T0/T1 merge  

## Agent-verified

| Check | Result |
|-------|--------|
| Challenge `execution_status` | `NOT_STARTED` |
| Challenge `status` | `PREREG_LOCKED` |
| CI on tip `91d1212` | green (`schemas-and-tests` ×2) |
| PR #37 draft | cleared — ready for review |
| Duplicate open stack PRs | closed |

## After human merge #37

1. Record actual `main` SHA + CI  
2. Update `REPO_SYNC_STATUS.md` + `RUN_STATE.tip`  
3. Do **not** start Challenge exec  

## Boundaries

`ATTR=NOT_SHOWN` · `M2=CLOSED` · `PRODUCTION_PROVEN=0` ·  
`CHALLENGE_EXEC=NOT_STARTED` · `CONTINUAL_SI=NOT_MEASURED`
