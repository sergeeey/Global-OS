# M-EXT3 public pack (identical for Arm A and Arm B)

Pinned task: encode/httpx#3614 — query corruption with `base_url` containing query string.

Contents:
- `ISSUE_SNAPSHOT.json` — issue body at pin (comments excluded)
- `PIN.json` — working SHA
- `repro_hint.md` — allowed starting point (issue's test case only)

Rules:
- Both arms use this pack only at start
- Do not read the other arm's workdir
- Do not polish M-EXT1 urllib3
