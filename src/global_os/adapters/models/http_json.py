"""Minimal JSON HTTP client for model adapters — stdlib only (no vendor SDK)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


class HttpJsonError(Exception):
    """Transport or HTTP-layer failure talking to a model endpoint."""

    def __init__(self, message: str, *, status: int | None = None, body: str = "") -> None:
        super().__init__(message)
        self.status = status
        self.body = body


def post_json(
    url: str,
    payload: dict[str, Any],
    *,
    headers: dict[str, str],
    timeout_seconds: float = 60.0,
) -> dict[str, Any]:
    """POST JSON and parse a JSON object response. Fail closed on errors."""
    data = json.dumps(payload).encode("utf-8")
    req_headers = {"Content-Type": "application/json", "Accept": "application/json", **headers}
    request = urllib.request.Request(url, data=data, headers=req_headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as resp:
            raw = resp.read().decode("utf-8")
            status = getattr(resp, "status", 200)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise HttpJsonError(
            f"HTTP {exc.code} from {url}: {body[:500]}",
            status=exc.code,
            body=body,
        ) from exc
    except urllib.error.URLError as exc:
        raise HttpJsonError(f"unreachable {url}: {exc.reason}") from exc
    except TimeoutError as exc:
        raise HttpJsonError(f"timeout talking to {url}") from exc

    if status >= 400:
        raise HttpJsonError(f"HTTP {status} from {url}: {raw[:500]}", status=status, body=raw)
    try:
        parsed: object = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as exc:
        raise HttpJsonError(f"non-JSON response from {url}: {raw[:200]}") from exc
    if not isinstance(parsed, dict):
        raise HttpJsonError(f"expected JSON object from {url}, got {type(parsed).__name__}")
    return parsed
