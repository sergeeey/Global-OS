"""Minimal OpenTelemetry tracing — Goal → OrgUnit → Task → Action hierarchy."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

_EXPORTER: InMemorySpanExporter | None = None
_CONFIGURED = False
_OTLP_CONFIGURED = False

REQUIRED_ATTR_KEYS = (
    "goal.id",
    "goal.version",
    "mission.id",
    "task.id",
    "org_unit.id",
    "principal.id",
)


class OtlpExportError(Exception):
    """Fail-closed when OTLP was requested but cannot be configured."""


def configure_tracing(*, service_name: str = "global-os") -> InMemorySpanExporter:
    """Idempotent local tracer setup. In-memory exporter for tests/CI evidence."""
    global _EXPORTER, _CONFIGURED
    if _CONFIGURED and _EXPORTER is not None:
        return _EXPORTER
    exporter = InMemorySpanExporter()
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    _EXPORTER = exporter
    _CONFIGURED = True
    return exporter


def configure_otlp_exporter(
    *,
    endpoint: str | None = None,
    service_name: str = "global-os",
) -> None:
    """Attach OTLP HTTP exporter when endpoint provided. Never silently no-ops.

    Requires optional dependency ``opentelemetry-exporter-otlp-proto-http``.
    If endpoint is set but package/connect config fails → OtlpExportError.
    """
    import os

    global _OTLP_CONFIGURED
    ep = endpoint if endpoint is not None else os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "")
    ep = (ep or "").strip()
    if not ep:
        raise OtlpExportError("OTEL_EXPORTER_OTLP_ENDPOINT unset; refusing silent pretend-export")
    try:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    except ImportError as exc:
        raise OtlpExportError(
            "opentelemetry-exporter-otlp-proto-http not installed; "
            "refusing silent in-memory-only fallback while OTLP was requested"
        ) from exc

    if not _CONFIGURED:
        configure_tracing(service_name=service_name)
    provider = trace.get_tracer_provider()
    if not isinstance(provider, TracerProvider):
        raise OtlpExportError("tracer provider is not SDK TracerProvider")
    exporter = OTLPSpanExporter(endpoint=ep)
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    _OTLP_CONFIGURED = True


def otlp_configured() -> bool:
    return _OTLP_CONFIGURED


def get_tracer(name: str = "global_os") -> trace.Tracer:
    if not _CONFIGURED:
        configure_tracing()
    return trace.get_tracer(name)


def clear_spans() -> None:
    if _EXPORTER is not None:
        _EXPORTER.clear()


def exported_spans() -> tuple[ReadableSpan, ...]:
    if _EXPORTER is None:
        return ()
    return tuple(_EXPORTER.get_finished_spans())


@contextmanager
def span(
    name: str,
    *,
    kind: str,
    attributes: dict[str, Any] | None = None,
) -> Iterator[trace.Span]:
    """Start a span with Global OS telemetry attributes.

    Full prompts/results are intentionally not logged (SPEC §66).
    """
    tracer = get_tracer()
    attrs = {"gos.span.kind": kind, **(attributes or {})}
    with tracer.start_as_current_span(name, attributes=attrs) as current:
        yield current


def goal_span(
    *,
    goal_id: str,
    goal_version: int,
    mission_id: str = "",
) -> Any:
    return span(
        f"goal:{goal_id}",
        kind="Goal",
        attributes={
            "goal.id": goal_id,
            "goal.version": goal_version,
            "mission.id": mission_id or goal_id,
        },
    )


def task_span(
    *,
    goal_id: str,
    goal_version: int,
    task_id: str,
    org_unit_id: str,
    principal_id: str,
) -> Any:
    return span(
        f"task:{task_id}",
        kind="Task",
        attributes={
            "goal.id": goal_id,
            "goal.version": goal_version,
            "mission.id": goal_id,
            "task.id": task_id,
            "org_unit.id": org_unit_id,
            "principal.id": principal_id,
        },
    )


def action_span(
    *,
    goal_id: str,
    goal_version: int,
    task_id: str,
    org_unit_id: str,
    principal_id: str,
    action_id: str,
    tool_id: str = "",
    policy_decision: str = "",
) -> Any:
    return span(
        f"action:{action_id}",
        kind="Action",
        attributes={
            "goal.id": goal_id,
            "goal.version": goal_version,
            "mission.id": goal_id,
            "task.id": task_id,
            "org_unit.id": org_unit_id,
            "principal.id": principal_id,
            "action.id": action_id,
            "tool.id": tool_id,
            "policy.decision": policy_decision,
        },
    )


def workflow_span(
    *,
    goal_id: str,
    run_id: str,
    workflow_name: str,
) -> Any:
    return span(
        f"workflow:{workflow_name}",
        kind="Workflow",
        attributes={
            "goal.id": goal_id,
            "workflow.run_id": run_id,
            "workflow.name": workflow_name,
            "runtime": "temporal",
        },
    )


def activity_span(
    *,
    goal_id: str,
    run_id: str,
    step_name: str,
) -> Any:
    return span(
        f"activity:{step_name}",
        kind="Activity",
        attributes={
            "goal.id": goal_id,
            "workflow.run_id": run_id,
            "activity.step": step_name,
            "runtime": "temporal",
        },
    )
