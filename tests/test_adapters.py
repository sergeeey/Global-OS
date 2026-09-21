from __future__ import annotations

from global_os.adapters.models import EchoModelProvider, GenerateRequest
from global_os.adapters.tools import FakeReadTool, ToolInvocation


def test_model_calls_go_through_provider_abstraction():
    provider = EchoModelProvider()
    resp = provider.generate(GenerateRequest(prompt="hello world"))
    assert resp.text.startswith("echo:")
    assert resp.model.provider == "stub"


def test_tool_adapter_contract():
    tool = FakeReadTool()
    out = tool.invoke(
        ToolInvocation(
            tool_id="fake.read",
            operation="fetch",
            arguments={"url": "https://example.com"},
            execution_token="tok_test",
            idempotency_key="idem-1",
        )
    )
    assert out.success is True
    assert tool.spec().required_capabilities == ("web.read",)
