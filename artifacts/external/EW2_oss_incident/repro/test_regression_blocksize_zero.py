"""Regression for urllib3#5248 — must FAIL before patch, PASS after.

Expects: HTTPConnection(..., blocksize=0) raises ValueError before any silent
empty upload when body is file-like.
"""

from __future__ import annotations

import socket
import tempfile
import threading
from pathlib import Path

import pytest
from urllib3.connection import HTTPConnection

PAYLOAD = b"SECRET_PAYLOAD_C3_BLOCKSIZE_ZERO"


def test_blocksize_zero_rejects_file_like_body() -> None:
    with pytest.raises(ValueError, match="blocksize must be > 0"):
        HTTPConnection("127.0.0.1", 9, blocksize=0, timeout=1)


def test_default_blocksize_still_sends_file_body() -> None:
    captured: list[bytes] = []
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    srv.listen(2)
    port = srv.getsockname()[1]

    def serve() -> None:
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
        c.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
        c.close()

    threading.Thread(target=serve, daemon=True).start()
    path = Path(tempfile.mkdtemp()) / "upload.bin"
    path.write_bytes(PAYLOAD)
    conn = HTTPConnection("127.0.0.1", port, timeout=5)
    with path.open("rb") as fh:
        conn.request("POST", "/upload", body=fh)
    conn.getresponse().read()
    conn.close()
    srv.close()
    assert PAYLOAD in captured[0]
