"""EW2 repro matrix for urllib3#5248 — blocksize vs file-like body."""

from __future__ import annotations

import json
import socket
import sys
import tempfile
import threading
from pathlib import Path

# Expect urllib3 on PYTHONPATH (pinned worktree)
from urllib3.connection import HTTPConnection

PAYLOAD = b"SECRET_PAYLOAD_C3_BLOCKSIZE_ZERO"
BLOCKSIZES = [None, 16384, 8192, 1, 0]  # None = constructor default


def run_matrix() -> dict:
    captured: list[bytes] = []
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    srv.listen(8)
    port = srv.getsockname()[1]

    def serve() -> None:
        for _ in range(len(BLOCKSIZES)):
            c, _ = srv.accept()
            c.settimeout(1)
            buf = b""
            try:
                while True:
                    chunk = c.recv(65536)
                    if not chunk:
                        break
                    buf += chunk
                    if b"\r\n\r\n" in buf:
                        c.settimeout(0.2)
            except OSError:
                pass
            captured.append(buf)
            c.sendall(
                b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
            )
            c.close()

    threading.Thread(target=serve, daemon=True).start()
    path = Path(tempfile.mkdtemp()) / "upload.bin"
    path.write_bytes(PAYLOAD)

    results = []
    for bs in BLOCKSIZES:
        kwargs = {"timeout": 5}
        if bs is not None:
            kwargs["blocksize"] = bs
        conn = HTTPConnection("127.0.0.1", port, **kwargs)
        with path.open("rb") as fh:
            conn.request("POST", "/upload", body=fh)
        conn.getresponse().read()
        conn.close()
        wire = captured[len(results)]
        has_payload = PAYLOAD in wire
        te_chunked = b"Transfer-Encoding: chunked" in wire
        # empty chunked body ends with 0\r\n\r\n after headers
        empty_chunked = te_chunked and (b"\r\n0\r\n\r\n" in wire) and not has_payload
        results.append(
            {
                "blocksize": bs if bs is not None else "default",
                "payload_on_wire": has_payload,
                "transfer_encoding_chunked": te_chunked,
                "silent_empty_chunked_body": empty_chunked,
                "wire_len": len(wire),
                "wire_tail_hex": wire[-80:].hex(),
                "wire_utf8_lossy": wire.decode("utf-8", errors="replace"),
            }
        )

    srv.close()
    bug_repro = any(
        r["blocksize"] == 0 and r["silent_empty_chunked_body"] for r in results
    )
    default_ok = any(
        r["blocksize"] in ("default", 16384) and r["payload_on_wire"] for r in results
    )
    return {
        "payload": PAYLOAD.decode(),
        "results": results,
        "bug_reproduced": bug_repro,
        "default_sends_payload": default_ok,
    }


def main() -> int:
    out = run_matrix()
    print(json.dumps(out, indent=2))
    return 0 if out["bug_reproduced"] and out["default_sends_payload"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
