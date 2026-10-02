# Arm A notes (minimal)

Looked at `BaseClient._enforce_trailing_slash`: it appends `/` to `url.raw_path`.
`URL.raw_path` is `path + ?query`, so `?data=1` becomes `?data=1/`.

Fix: slash `url.path` only via `copy_with(path=...)`.

Countercheck: path-only base_url still gets trailing slash (existing property).
