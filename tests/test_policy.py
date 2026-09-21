from __future__ import annotations

from global_os.kernel.policy import PolicyEngine, PolicyRequest


def test_cedar_aligned_default_deny_and_approval():
    engine = PolicyEngine()
    deny = engine.decide(
        PolicyRequest(
            principal="w1",
            action="email.send",
            resource="smtp",
            capability="email.send",
            granted_capabilities=frozenset({"email.send"}),
            approval_id=None,
        )
    )
    assert deny.allowed is False
    allow = engine.decide(
        PolicyRequest(
            principal="w1",
            action="web.read",
            resource="https://x",
            capability="web.read",
            granted_capabilities=frozenset({"web.read"}),
        )
    )
    assert allow.allowed is True
    forbidden = engine.decide(
        PolicyRequest(
            principal="w1",
            action="Bash(*)",
            resource="*",
            capability="Bash(*)",
            granted_capabilities=frozenset({"Bash(*)"}),
        )
    )
    assert forbidden.allowed is False
