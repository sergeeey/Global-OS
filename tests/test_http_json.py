"""HTTP JSON client + API key sanitization."""

from __future__ import annotations

from global_os.adapters.models.http_json import sanitize_api_key


def test_sanitize_api_key_strips_bom_quotes_zwsp():
    raw = "\ufeff\"sk-or-test\u200b\"\n"
    assert sanitize_api_key(raw) == "sk-or-test"
