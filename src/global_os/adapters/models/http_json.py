"""Minimal JSON HTTP client for model adapters — stdlib only (no vendor SDK)."""

from __future__ import annotations

import json
import math
import os
import sys
import threading
import time
import urllib.error
import urllib.request
from typing import Any

# Cloudflare / WAF often block the default Python-urllib User-Agent (e.g. Groq 1010).
_DEFAULT_UA = "GlobalOS/0.1 (+https://github.com/sergeeey/Global-OS; compatible)"

# Transient provider / gateway pressure — bounded (never unbounded).
_RETRYABLE_STATUS = frozenset({429, 503})
_DEFAULT_MAX_ATTEMPTS = 4  # 1 try + up to 3 retries
_MAX_BACKOFF_SECONDS = 60.0
_BASE_BACKOFF_SECONDS = 1.0
# Groq free on_demand RPM ≈ 30 → ≥2s spacing avoids 429 storms on long evals.
_GROQ_DEFAULT_MIN_INTERVAL = 2.1
_QUOTA_BODY_MARKERS = (
    "tokens per day",
    "requests per day",
    " on tpd",
    " on rpd",
    "tpd):",
    "rpd):",
)

_pace_lock = threading.Lock()
_next_slot_monotonic = 0.0


def is_daily_quota_error(body: str) -> bool:
    """True when provider signals day-window quota (retrying wastes wall clock)."""
    b = body.lower()
    return any(marker in b for marker in _QUOTA_BODY_MARKERS)


class HttpJsonError(Exception):
    """Transport or HTTP-layer failure talking to a model endpoint."""

    def __init__(
        self,
        message: str,
        *,
        status: int | None = None,
        body: str = "",
        retry_after: float | None = None,
        attempts: int = 1,
        quota_exhausted: bool = False,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.body = body
        self.retry_after = retry_after
        self.attempts = attempts
        self.quota_exhausted = quota_exhausted


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


def parse_retry_after(raw: str | None) -> float | None:
    """Parse Retry-After as delay-seconds. Ignore HTTP-date forms."""
    if raw is None:
        return None
    text = raw.strip()
    if not text:
        return None
    try:
        seconds = float(text)
    except ValueError:
        return None
    if seconds < 0 or math.isnan(seconds):
        return None
    return float(min(seconds, _MAX_BACKOFF_SECONDS))


def _backoff_seconds(attempt: int, *, retry_after: float | None) -> float:
    """attempt is 0-based index of the failed try."""
    if retry_after is not None:
        return float(min(max(retry_after, 0.0), _MAX_BACKOFF_SECONDS))
    return float(min(_BASE_BACKOFF_SECONDS * (2**attempt), _MAX_BACKOFF_SECONDS))


def _min_interval_for_url(url: str) -> float:
    """Optional global pacing. Env overrides; Groq free-tier gets a safe default."""
    raw = os.environ.get("GOS_MODEL_HTTP_MIN_INTERVAL_SECONDS", "").strip()
    if raw:
        try:
            return max(0.0, float(raw))
        except ValueError as exc:
            raise ValueError(
                f"GOS_MODEL_HTTP_MIN_INTERVAL_SECONDS must be float, got {raw!r}"
            ) from exc
    if "api.groq.com" in url:
        return _GROQ_DEFAULT_MIN_INTERVAL
    return 0.0


def _acquire_request_slot(url: str) -> None:
    """Serialize / space outbound model POSTs (process-local). Never unbounded."""
    global _next_slot_monotonic
    interval = _min_interval_for_url(url)
    if interval <= 0:
        return
    with _pace_lock:
        now = time.monotonic()
        wait = _next_slot_monotonic - now
        if wait > 0:
            time.sleep(wait)
            now = time.monotonic()
        _next_slot_monotonic = now + interval


def _log_retry(url: str, *, status: int, attempt: int, delay: float) -> None:
    if os.environ.get("GOS_HTTP_DEBUG", "").strip() not in {"1", "true", "TRUE", "yes"}:
        return
    print(
        f"[http_json] retry status={status} attempt={attempt} delay={delay:.2f}s url={url}",
        file=sys.stderr,
        flush=True,
    )


def post_json(
    url: str,
    payload: dict[str, Any],
    *,
    headers: dict[str, str],
    timeout_seconds: float = 60.0,
    max_attempts: int = _DEFAULT_MAX_ATTEMPTS,
) -> dict[str, Any]:
    """POST JSON and parse a JSON object response. Fail closed on errors.

    Retries only on HTTP 429/503 with exponential backoff (honors Retry-After
    when present as delay-seconds). Attempts are hard-capped — never unbounded.
    Groq free-tier URLs are paced (~2.1s) to stay under RPM=30 unless overridden.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")

    data = json.dumps(payload).encode("utf-8")
    req_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": _DEFAULT_UA,
        **headers,
    }

    last_error: HttpJsonError | None = None
    for attempt in range(max_attempts):
        _acquire_request_slot(url)
        request = urllib.request.Request(url, data=data, headers=req_headers, method="POST")
        try:
            with _OPENER.open(request, timeout=timeout_seconds) as resp:
                raw = resp.read().decode("utf-8")
                status = getattr(resp, "status", 200)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            retry_after = parse_retry_after(exc.headers.get("Retry-After") if exc.headers else None)
            quota = is_daily_quota_error(body)
            err = HttpJsonError(
                f"HTTP {exc.code} from {url}: {body[:500]}",
                status=exc.code,
                body=body,
                retry_after=retry_after,
                attempts=attempt + 1,
                quota_exhausted=quota,
            )
            # Day-window TPD/RPD: fail closed immediately (retrying burns hours).
            if quota:
                raise err from exc
            if exc.code in _RETRYABLE_STATUS and attempt + 1 < max_attempts:
                delay = _backoff_seconds(attempt, retry_after=retry_after)
                _log_retry(url, status=exc.code, attempt=attempt + 1, delay=delay)
                time.sleep(delay)
                last_error = err
                continue
            raise err from exc
        except urllib.error.URLError as exc:
            raise HttpJsonError(
                f"unreachable {url}: {exc.reason}",
                attempts=attempt + 1,
            ) from exc
        except TimeoutError as exc:
            raise HttpJsonError(
                f"timeout talking to {url}",
                attempts=attempt + 1,
            ) from exc

        if status >= 400:
            quota = is_daily_quota_error(raw)
            err = HttpJsonError(
                f"HTTP {status} from {url}: {raw[:500]}",
                status=status,
                body=raw,
                attempts=attempt + 1,
                quota_exhausted=quota,
            )
            if quota:
                raise err
            if status in _RETRYABLE_STATUS and attempt + 1 < max_attempts:
                delay = _backoff_seconds(attempt, retry_after=None)
                _log_retry(url, status=status, attempt=attempt + 1, delay=delay)
                time.sleep(delay)
                last_error = err
                continue
            raise err

        try:
            parsed: object = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError as exc:
            raise HttpJsonError(
                f"non-JSON response from {url}: {raw[:200]}",
                attempts=attempt + 1,
            ) from exc
        if not isinstance(parsed, dict):
            raise HttpJsonError(
                f"expected JSON object from {url}, got {type(parsed).__name__}",
                attempts=attempt + 1,
            )
        return parsed

    # Unreachable if max_attempts >= 1, but keep fail-closed.
    if last_error is not None:
        raise last_error
    raise HttpJsonError(f"no response from {url}", attempts=max_attempts)
