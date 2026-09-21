"""Minimal OTLP HTTP sink for Reality Contact tests (no Docker required)."""

from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any


@dataclass
class OtlpHttpSink:
    host: str = "127.0.0.1"
    port: int = 0
    posts: list[dict[str, Any]] = field(default_factory=list)
    _httpd: HTTPServer | None = None
    _thread: threading.Thread | None = None

    @property
    def endpoint(self) -> str:
        assert self._httpd is not None
        host, port = self._httpd.server_address[:2]
        return f"http://{host}:{port}/v1/traces"

    @property
    def base_url(self) -> str:
        assert self._httpd is not None
        host, port = self._httpd.server_address[:2]
        return f"http://{host}:{port}"

    def start(self) -> None:
        sink = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length)
                sink.posts.append(
                    {
                        "path": self.path,
                        "content_type": self.headers.get("Content-Type", ""),
                        "bytes": body,
                        "size": len(body),
                    }
                )
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b"{}")

            def log_message(self, format: str, *args: object) -> None:
                return

        self._httpd = HTTPServer((self.host, self.port), Handler)
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._httpd is not None:
            self._httpd.shutdown()
            self._httpd.server_close()
        if self._thread is not None:
            self._thread.join(timeout=5)


@contextmanager
def otlp_http_sink() -> Iterator[OtlpHttpSink]:
    sink = OtlpHttpSink()
    sink.start()
    try:
        yield sink
    finally:
        sink.stop()
