"""In-process OpenAI + Anthropic HTTP mocks for Reality Contact wire tests."""

from __future__ import annotations

import json
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any


@dataclass
class ModelHttpSink:
    kind: str  # "openai" | "anthropic"
    host: str = "127.0.0.1"
    port: int = 0
    posts: list[dict[str, Any]] = field(default_factory=list)
    response_text: str = "wire-ok"
    # Optional queue of HTTP status codes (popped per POST). Empty → always 200.
    status_sequence: list[int] = field(default_factory=list)
    retry_after_seconds: float | None = None
    _httpd: HTTPServer | None = None
    _thread: threading.Thread | None = None

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
                        "headers": {k: v for k, v in self.headers.items()},
                        "body": body,
                    }
                )
                status = 200
                if sink.status_sequence:
                    status = int(sink.status_sequence.pop(0))
                if status >= 400:
                    err_body = json.dumps(
                        {"error": {"message": f"mock {status}", "type": "rate_limit"}}
                    ).encode("utf-8")
                    self.send_response(status)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(err_body)))
                    if sink.retry_after_seconds is not None:
                        self.send_header("Retry-After", str(sink.retry_after_seconds))
                    self.end_headers()
                    self.wfile.write(err_body)
                    return
                if sink.kind == "openai":
                    req_model = "gpt-4o-mini-wire"
                    try:
                        parsed_body = json.loads(body.decode("utf-8") or "{}")
                        if isinstance(parsed_body, dict) and parsed_body.get("model"):
                            req_model = str(parsed_body["model"])
                    except json.JSONDecodeError:
                        pass
                    payload = {
                        "id": "chatcmpl-wire",
                        "model": req_model,
                        "choices": [
                            {
                                "index": 0,
                                "message": {"role": "assistant", "content": sink.response_text},
                                "finish_reason": "stop",
                            }
                        ],
                        "usage": {"prompt_tokens": 11, "completion_tokens": 3, "total_tokens": 14},
                    }
                else:
                    payload = {
                        "id": "msg_wire",
                        "model": "claude-3-5-haiku-latest",
                        "type": "message",
                        "role": "assistant",
                        "content": [{"type": "text", "text": sink.response_text}],
                        "usage": {"input_tokens": 9, "output_tokens": 4},
                    }
                raw = json.dumps(payload).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

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
def model_http_sink(
    kind: str,
    *,
    response_text: str = "wire-ok",
    status_sequence: list[int] | None = None,
    retry_after_seconds: float | None = None,
) -> Iterator[ModelHttpSink]:
    sink = ModelHttpSink(
        kind=kind,
        response_text=response_text,
        status_sequence=list(status_sequence or []),
        retry_after_seconds=retry_after_seconds,
    )
    sink.start()
    try:
        yield sink
    finally:
        sink.stop()
