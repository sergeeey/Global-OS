"""Minimal JSON HTTP client for model adapters — stdlib only (no vendor SDK)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

# Cloudflare / WAF often block the default Python-urllib User-Agent (e.g. Groq 1010).
_DEFAULT_UA = "GlobalOS/0.1 (+https://github.com/sergeeey/Global-OS; compatible)"


class HttpJsonError(Exception):
    """Transport or HTTP-layer failure talking to a model endpoint."""

    def __init__(self, message: str, *, status: int | None = None, body: str = "") -> None:
        super().__init__(message)
        self.status = status
        self.body = body


class _KeepAuthRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Preserve Authorization across redirects (stdlib strips it by default)."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new is None:
            return None
        auth = req.get_header("Authorization")
        if auth and new.get_header("Authorization") is None:
            new.add_header("Authorization", auth)
        return new


_OPENER = urllib.request.build_opener(_KeepAuthRedirectHandler)


def sanitize_api_key(value: str) -> str:
    """Strip quotes/BOM/zero-width junk from env-loaded secrets."""
    v = value.strip()
    for ch in ("\ufeff", "\u200b", "\u200c", "\u200d"):
        v = v.replace(ch, "")
    v = v.strip().strip('"').strip("'").strip()
    return v


def post_json(
    url: str,
    payload: dict[str, Any],
    *,
    headers: dict[str, str],
    timeout_seconds: float = 60.0,
) -> dict[str, Any]:
    """POST JSON and parse a JSON object response. Fail closed on errors."""
    data = json.dumps(payload).encode("utf-8")
    req_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": _DEFAULT_UA,
        **headers,
    }
    request = urllib.request.Request(url, data=data, headers=req_headers, method="POST")
    try:
        with _OPENER.open(request, timeout=timeout_seconds) as resp:
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
