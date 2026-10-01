# EW2 Competing explanations — urllib3#5248

**Working SHA:** `796d200d3070ead69ec3a5d848fecf52a2249b59`  
**Repro:** `repro/logs/matrix_796d200.json`, `repro/logs/issue_exact_script.txt`

## Matrix summary

| blocksize | payload on wire (contiguous) | notes |
|-----------|------------------------------|-------|
| default / 16384 / 8192 | yes | OK |
| 1 | yes (chunked 1-byte frames) | OK; contiguous search may miss |
| 0 | **no** — empty chunked `0\r\n\r\n` | **BUG** |

## H1 — `H_zero_blocksize_read_loop` (PRIMARY)

**Claim:** `body.read(0)` returns `b""` immediately, so `chunk_readable()` in
`urllib3.util.request.body_to_chunks` breaks without sending data, while still
framing as `Transfer-Encoding: chunked`.

**Confirming:**
- Source: `util/request.py` `datablock = body.read(blocksize)` + `if not datablock: break`
- Python semantics: `open(...).read(0) == b""`
- Wire: `blocksize=0` → headers + `0\r\n\r\n` only (repro logs)

**Disconfirming test for alternatives:** see H2–H4 below.

**Status:** **SUPPORTED** (pending hard gate with patch+regression)

## H2 — `H_body_already_consumed`

**Claim:** body was consumed earlier; blocksize incidental.

**Disconfirming:** each `post()` opens a fresh `path.open("rb")`; default/16384
sends full payload from same on-disk file in the same process.

**Status:** **REJECTED**

## H3 — `H_http2_or_proxy_path`

**Claim:** only HTTP/2 or proxy adapters drop the body.

**Disconfirming:** repro uses `urllib3.connection.HTTPConnection` directly over
plain HTTP/1.1 to a local socket server — no proxy, no HTTP/2.

**Status:** **REJECTED**

## H4 — `H_not_reproducible`

**Claim:** cannot reproduce on pinned revision.

**Disconfirming:** reproduced on pin SHA (exact issue script + matrix).

**Status:** **REJECTED**
