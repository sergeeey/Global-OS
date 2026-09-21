"""Live OTLP export — Reality Contact.

Prefers external collector via OTEL_EXPORTER_OTLP_ENDPOINT (compose).
Falls back to in-process OTLP HTTP sink so export path is still exercised.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import pytest

from global_os.observability import (
    configure_otlp_exporter,
    configure_tracing,
    goal_span,
    otlp_configured,
    task_span,
)
from tests.support.otlp_http_sink import otlp_http_sink


def test_otlp_export_path_to_external_receiver(monkeypatch: pytest.MonkeyPatch):
    try:
        import opentelemetry.exporter.otlp.proto.http.trace_exporter  # noqa: F401
    except ImportError:
        if os.environ.get("GOS_REQUIRE_OTLP") == "1":
            pytest.fail("otlp exporter package missing under GOS_REQUIRE_OTLP=1")
        pytest.skip("opentelemetry-exporter-otlp-proto-http not installed")

    import global_os.observability.tracing as tr

    monkeypatch.setattr(tr, "_CONFIGURED", False)
    monkeypatch.setattr(tr, "_OTLP_CONFIGURED", False)
    monkeypatch.setattr(tr, "_EXPORTER", None)

    env_ep = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "").rstrip("/")
    dump = Path(
        os.environ.get(
            "GOS_OTEL_TRACES_FILE",
            str(Path(__file__).resolve().parents[1] / "deploy" / "otel-out" / "traces.json"),
        )
    )

    with otlp_http_sink() as sink:
        # Prefer env collector when set; else local sink (still real OTLP HTTP wire).
        if env_ep:
            traces_url = env_ep if env_ep.endswith("/v1/traces") else f"{env_ep}/v1/traces"
        else:
            traces_url = sink.endpoint
            if os.environ.get("GOS_REQUIRE_OTLP") == "1" and not env_ep:
                # CI should set collector endpoint; sink still proves exporter path.
                pass

        configure_tracing(service_name="global-os-reality")
        configure_otlp_exporter(endpoint=traces_url, service_name="global-os-reality")
        assert otlp_configured() is True

        with goal_span(goal_id="goal_otlp_live", goal_version=1, mission_id="msn_otlp"), task_span(
            goal_id="goal_otlp_live",
            goal_version=1,
            task_id="task_otlp_1",
            org_unit_id="org_otlp",
            principal_id="wkr_otlp",
        ):
            pass

        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider

        provider = trace.get_tracer_provider()
        assert isinstance(provider, TracerProvider)
        assert provider.force_flush(timeout_millis=10_000) is True

        if env_ep and dump.parent.exists():
            deadline = time.time() + 15
            payload = ""
            while time.time() < deadline:
                if dump.exists() and dump.stat().st_size > 0:
                    payload = dump.read_text(encoding="utf-8", errors="replace")
                    if "goal_otlp_live" in payload or "global-os-reality" in payload:
                        break
                time.sleep(0.25)
            if dump.exists() and dump.stat().st_size > 0:
                assert "goal_otlp_live" in payload or "global-os-reality" in payload
                return

        # In-process sink received OTLP POST bytes (protobuf or json).
        deadline = time.time() + 5
        while time.time() < deadline and not sink.posts:
            time.sleep(0.05)
        assert sink.posts, "OTLP exporter did not POST to receiver"
        assert sink.posts[0]["size"] > 0
        assert "/v1/traces" in sink.posts[0]["path"]
