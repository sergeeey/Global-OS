# EW2 — Live OSS Incident Investigation

**Status:** `PREREG_LOCKED`  
**Protocol id:** `EW2-OSS-v1`  
**Mission id:** `EW2`  
**Date (UTC):** 2026-10-01

## Target (pinned before investigation claims)

| Field | Value |
|-------|--------|
| Repository | `urllib3/urllib3` |
| Issue | [#5248](https://github.com/urllib3/urllib3/issues/5248) |
| Title | `HTTPConnection(blocksize=0)` silently drops file-like request bodies |
| State at pin | OPEN (verify at run time) |
| Why chosen | Claimed **silent data loss** — high external value; root cause not assumed |

Alternate (not started): `encode/httpx#3782` (AsyncClient.stream double-cancel leak).

## Goal

Reproduce the problem, build **competing explanations**, identify root cause with
counterevidence search, and propose a **testable fix** — without treating Global OS
self-metrics as success.

## Competing explanations (initial set; amend only before “root cause claim”)

1. **H_zero_blocksize_read_loop** — `blocksize=0` makes the read/send loop terminate
   immediately / skip body chunks, so file-like bodies are never uploaded.
2. **H_body_already_consumed** — body was consumed earlier; `blocksize=0` is incidental.
3. **H_http2_or_proxy_path** — only some adapters/paths drop the body; HTTP/1.1 direct
   path is fine.
4. **H_not_reproducible** — cannot reproduce on pinned urllib3 revision → INCONCLUSIVE.

## Strong baseline / null

- Document expected urllib3 behavior from docs + source for `blocksize`.
- Compare `blocksize=None` / default vs `blocksize=0` with identical file-like body.

## Preregistered procedure

1. Pin urllib3 commit SHA at investigation start (`EW2_PIN.json`).
2. Write minimal repro script (no Global OS changes required).
3. Record: OS, Python, urllib3 SHA, HTTP target (local dummyserver or httpbin).
4. Test matrix: file-like body × blocksize ∈ {default, 0, 1, 8192}.
5. For each competing H: list confirming observation + **disconfirming** test.
6. Only then claim root cause / propose patch + regression test.

## Decision vocabulary

| Verdict | Meaning |
|---------|---------|
| `ROOT_CAUSE_CONFIRMED` | Repro + mechanism + counterevidence tests pass; fix proposal testable |
| `REJECTED` | Primary H fails; another H confirmed or issue not as stated |
| `INCONCLUSIVE` | Cannot reproduce / env block / insufficient access |

## Forbidden

- Edit Global OS to make the investigation “look better”
- Cite Y24/Y25 as evidence about urllib3
- Claim fix merged upstream without upstream review
- Scope creep into unrelated urllib3 issues without new pin

## Deliverables

- `EW2_PIN.json` — repo/issue/commit pin
- `repro/` — scripts + logs
- `COMPETING_EXPLANATIONS.md`
- `ROOT_CAUSE.md` or honest `INCONCLUSIVE.md`
- optional `proposed_fix.diff` + test sketch (upstream-oriented)
