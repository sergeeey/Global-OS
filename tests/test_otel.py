from __future__ import annotations

from global_os.observability import (
    action_span,
    clear_spans,
    configure_tracing,
    exported_spans,
    goal_span,
    task_span,
)


def test_otel_goal_task_action_hierarchy():
    configure_tracing()
    clear_spans()
    with goal_span(goal_id="goal_x", goal_version=1, mission_id="mission_x"), task_span(
        goal_id="goal_x",
        goal_version=1,
        task_id="task_1",
        org_unit_id="org_1",
        principal_id="wkr_1",
    ), action_span(
        goal_id="goal_x",
        goal_version=1,
        task_id="task_1",
        org_unit_id="org_1",
        principal_id="wkr_1",
        action_id="act_1",
        tool_id="fake.read",
        policy_decision="ALLOW",
    ):
        pass
    spans = exported_spans()
    kinds = {s.attributes.get("gos.span.kind") for s in spans if s.attributes}
    assert kinds == {"Goal", "Task", "Action"}
    action = next(s for s in spans if s.attributes and s.attributes.get("gos.span.kind") == "Action")
    assert action.attributes is not None
    assert action.attributes["goal.id"] == "goal_x"
    assert action.attributes["task.id"] == "task_1"
    assert action.attributes["policy.decision"] == "ALLOW"
    # No prompt dumping by default
    assert "prompt" not in action.attributes
