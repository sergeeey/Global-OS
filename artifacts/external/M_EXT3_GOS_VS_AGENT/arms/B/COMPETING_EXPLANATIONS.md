# Competing explanations — httpx#3614

## H1 — `H_raw_path_trailing_slash`

`BaseClient._enforce_trailing_slash` appends `/` to `URL.raw_path`.  
`raw_path` includes `?query`, so `data=1` becomes `data=1/`.

## H2 — `H_merge_url_join`

Corruption happens only when merging relative request URL with `base_url`
in `_merge_url` / `build_request`.

## H3 — `H_urlparse_artifact`

`URL` / urlparse quoting invents the trailing slash independent of Client.

## H4 — `H_not_reproducible`

Cannot reproduce on pinned SHA → INCONCLUSIVE.

## Strong baseline / null

`URL("https://host/get?data=1")` alone must keep `query == b"data=1"`.  
Path-only `base_url` must still receive trailing slash after any fix.
