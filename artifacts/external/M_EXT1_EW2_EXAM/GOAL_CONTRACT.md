# M-EXT1 — Goal Contract (EW2 exam)

**Status:** `GOAL_LOCKED`  
**Exam id:** `M-EXT1-EW2`  
**Protocol:** `EW2-OSS-v1`  
**Target:** urllib3#5248

## Goal (external value)

Reproduce, explain, and (if confirmed) propose a testable fix for:

> `HTTPConnection(blocksize=0)` silently drops file-like request bodies

Success = honest terminal with upstream-ready artifacts — **not** “Global OS looks good”.

## Deliverable shape (upstream-ready)

1. Minimal repro script + logs  
2. Competing explanations + counterevidence  
3. Root-cause writeup **or** honest INCONCLUSIVE/REJECTED  
4. If `ROOT_CAUSE_CONFIRMED`: patch + regression test + limitations  

## Time / budget envelope (hard stop)

| Resource | Cap | On exhaust |
|----------|-----|------------|
| Wall investigation | **6 hours** cumulative agent work on this exam | honest stop → `INCONCLUSIVE` if no terminal claim |
| Repro/patch iterations | **40** scripted runs | stop; document |
| Manual hypothesis pivots | **8** | stop; document |
| Provider LLM cost | **$5** equivalent (if used) | stop using LLM; finish on local reasoning |
| Global OS code edits | **0** unless real mission failure forces ADR | forbidden for optics |

Ledger must record spent vs cap. “Ещё чуть-чуть исследовать” after envelope → **forbidden**.

## Hard gate for `ROOT_CAUSE_CONFIRMED`

All must hold:

1. Stable repro on pinned SHA (`blocksize=0` drops body; default does not).  
2. Mechanism identified with at least one **disconfirming** test for rejected alternatives.  
3. Local patch **eliminates** the silent drop on the repro.  
4. Regression test **fails before patch** and **passes after patch**.  

Missing any gate → cannot claim `ROOT_CAUSE_CONFIRMED` (use REJECTED/INCONCLUSIVE).

## Forbidden

- Change Global OS to improve exam optics  
- Cite Y24/Y25 as urllib3 evidence  
- Claim upstream merge  
- Open Y25-F2 / architecture from metaphor  
- Parallel-start EW1 during this exam  

## EW1

Remains queued until this exam terminals.
