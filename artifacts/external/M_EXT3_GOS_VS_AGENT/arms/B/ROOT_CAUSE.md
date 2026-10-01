# Root cause — encode/httpx#3614

**Terminal:** `ROOT_CAUSE_CONFIRMED`  
**Surviving hypothesis:** H1 `H_raw_path_trailing_slash`

## Mechanism

```text
Client(base_url=...)
  → _enforce_trailing_slash(URL)
  → raw_path.endswith(b"/")?  # raw_path == b"/get?data=1"
  → copy_with(raw_path=raw_path + b"/")
  → raw_path == b"/get?data=1/"
  → query value becomes "1/"
```

## Counterevidence

| H | Result | Evidence |
|---|--------|----------|
| H4 | REJECTED | stable repro on `b5addb6` (`counterevidence_matrix.txt`) |
| H3 | DISCONFIRMED | bare `URL(...)` keeps `query==b"data=1"` |
| H2 | DISCONFIRMED | `Client.base_url` already corrupt before `build_request` |
| H1 | CONFIRMED | `copy_with(raw_path=+/)` corrupts; `copy_with(path=+/)` preserves query |

## Fix

Enforce trailing slash on **path** only:

```python
if url.path.endswith("/"):
    return url
return url.copy_with(path=f"{url.path}/")
```

## Hard gate

- Repro: PASS  
- Counterevidence: PASS  
- Patch eliminates: PASS  
- Regression fail-before / pass-after: PASS (`workdir/repro/logs/`)
