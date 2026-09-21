from __future__ import annotations

import builtins
import sys

import pytest

from global_os.observability import (
    OtlpExportError,
    action_span,
    clear_spans,
    configure_otlp_exporter,
    configure_tracing,
    exported_spans,
    goal_span,
    task_span,
)


def test_otel_goal_task_action_hierarchy():
    configure_tracing()
    clear_spans()
    with (
        goal_span(goal_id="goal_x", goal_version=1, mission_id="mission_x"),
        task_span(
            goal_id="goal_x",
            goal_version=1,
            task_id="task_1",
            org_unit_id="org_1",
            principal_id="wkr_1",
        ),
        action_span(
            goal_id="goal_x",
            goal_version=1,
            task_id="task_1",
            org_unit_id="org_1",
            principal_id="wkr_1",
            action_id="act_1",
            tool_id="fake.read",
            policy_decision="ALLOW",
        ),
    ):
        pass
    spans = exported_spans()
    kinds = {s.attributes.get("gos.span.kind") for s in spans if s.attributes}
    assert kinds == {"Goal", "Task", "Action"}
    action = next(
        s for s in spans if s.attributes and s.attributes.get("gos.span.kind") == "Action"
    )
    assert action.attributes is not None
    assert action.attributes["goal.id"] == "goal_x"
    assert action.attributes["task.id"] == "task_1"
    assert action.attributes["policy.decision"] == "ALLOW"
    assert "prompt" not in action.attributes


def test_otlp_fails_closed_without_endpoint():
    with pytest.raises(OtlpExportError, match="unset"):
        configure_otlp_exporter(endpoint="")


def test_otlp_fails_closed_without_exporter_package(monkeypatch: pytest.MonkeyPatch):
    real_import = builtins.__import__

    def fake_import(name: str, *args: object, **kwargs: object):  # type: ignore[no-untyped-def]
        if "opentelemetry.exporter.otlp" in name:
            raise ImportError("mocked missing otlp exporter")
        return real_import(name, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(builtins, "__import__", fake_import)
    for key in list(sys.modules):
        if "opentelemetry.exporter.otlp" in key:
            sys.modules.pop(key, None)
    with pytest.raises(OtlpExportError, match="not installed"):
        configure_otlp_exporter(endpoint="http://127.0.0.1:4318/v1/traces")
