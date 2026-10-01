# EW2 Terminal — ROOT_CAUSE_CONFIRMED

**Exam:** `M-EXT1-EW2`  
**Issue:** https://github.com/urllib3/urllib3/issues/5248  
**Working SHA:** `796d200d3070ead69ec3a5d848fecf52a2249b59`  
**Verdict:** `ROOT_CAUSE_CONFIRMED`  
**Date (UTC):** 2026-10-01

## Mechanism

For file-like bodies, `urllib3.util.request.body_to_chunks` does:

```python
datablock = body.read(blocksize)
if not datablock:
    break
```

In Python, `file.read(0)` returns `b""` immediately. Therefore `blocksize=0`
exits the read loop without uploading any bytes, while the connection still
sends `Transfer-Encoding: chunked` with an empty body (`0\r\n\r\n`). No exception
is raised → **silent data loss**.

## Hard gate evidence

| Gate | Result |
|------|--------|
| Stable repro on pin SHA | PASS — `repro/logs/matrix_796d200.json`, `issue_exact_script.txt` |
| Alternatives disconfirmed | PASS — H2/H3/H4 REJECTED in `COMPETING_EXPLANATIONS.md` |
| Local patch eliminates silent drop | PASS — `blocksize=0` raises `ValueError`; default still sends payload |
| Regression fails before / passes after | PASS — `repro/logs/regression_BEFORE_patch.txt` (FAILED ValueError expected), `regression_AFTER_patch.txt` (2 passed) |

## Proposed fix (upstream-ready)

Reject `blocksize <= 0` early (`HTTPConnection.__init__`) and in
`body_to_chunks` for file-like bodies. Diff: `proposed_fix.diff`.

Alternative (not chosen): treat `0` as “read all” (`read()` / `read(-1)`). Reject
is clearer and matches issue’s first suggested behavior.

## Limitations

- Patch applied only in local worktree for verification; **not** submitted upstream here.
- HTTPSConnection / PoolManager paths inherit via same `blocksize` / `body_to_chunks`;
  constructor check covers `HTTPConnection`; `body_to_chunks` covers other callers.
- `blocksize=1` remains valid (inefficient but correct).
- Does not claim production deploy of Global OS; external urllib3 artifact only.

## Non-claims

- Not a Global OS architecture win  
- Y24/Y25 not used as evidence  
- Upstream merge not claimed  
