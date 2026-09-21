"""Recording wrapper — every model call lands in the event trail (GOS-I09/I17)."""

from __future__ import annotations

from typing import Any

from global_os.adapters.models.base import (
    GenerateRequest,
    GenerateResponse,
    ModelProvider,
    ModelProviderError,
)
from global_os.common.hashing import content_hash
from global_os.runtime.events.ledger import EventLedger


class RecordingModelProvider(ModelProvider):
    """Decorates a provider; appends model.invoked with model/version/cost/latency/output."""

    def __init__(
        self,
        inner: ModelProvider,
        ledger: EventLedger,
        *,
        tenant_id: str = "t",
        workspace_id: str = "w",
        goal_id: str | None = None,
        producer: str = "adapters.models.recording",
    ) -> None:
        self._inner = inner
        self._ledger = ledger
        self._tenant_id = tenant_id
        self._workspace_id = workspace_id
        self._goal_id = goal_id
        self._producer = producer
        self.calls: list[dict[str, Any]] = []

    @property
    def inner(self) -> ModelProvider:
        return self._inner

    def generate(self, request: GenerateRequest) -> GenerateResponse:
        try:
            resp = self._inner.generate(request)
        except ModelProviderError as exc:
            self._record_failure(request, str(exc))
            raise
        sub = getattr(self._inner, "last_substitution", None)
        if isinstance(sub, dict) and sub:
            self._ledger.append(
                event_type="model.substituted",
                tenant_id=self._tenant_id,
                workspace_id=self._workspace_id,
                goal_id=self._goal_id,
                payload=dict(sub),
                producer=self._producer,
            )
        from global_os.adapters.models.zero_cost import assert_zero_cost_allowed

        assert_zero_cost_allowed(
            cost_usd=resp.cost_usd,
            free_tier=resp.cost_usd == 0.0 or resp.cost_usd is None,
        )
        self._record_success(request, resp)
        return resp

    def structured_generate(
        self, request: GenerateRequest, schema: dict[str, Any]
    ) -> dict[str, Any]:
        try:
            out = self._inner.structured_generate(request, schema)
        except ModelProviderError as exc:
            self._record_failure(request, str(exc), structured=True)
            raise
        # Also emit trail for structured path via a synthetic response digest
        preview = str(out)[:200]
        payload = {
            "status": "ok",
            "mode": "structured",
            "provider": "unknown",
            "model": "unknown",
            "version": "unknown",
            "input_tokens": 0,
            "output_tokens": 0,
            "latency_ms": 0.0,
            "cost_usd": None,
            "output_digest": content_hash(out),
            "output_preview": preview,
            "prompt_digest": content_hash({"prompt": request.prompt}),
        }
        # Prefer inner model_ref when available
        ref = getattr(self._inner, "model_ref", None)
        if ref is not None:
            payload["provider"] = ref.provider
            payload["model"] = ref.model
            payload["version"] = ref.version
        self._append(payload)
        return out

    def _record_success(self, request: GenerateRequest, resp: GenerateResponse) -> None:
        payload = {
            "status": "ok",
            "mode": "generate",
            "provider": resp.model.provider,
            "model": resp.model.model,
            "version": resp.model.version,
            "input_tokens": resp.input_tokens,
            "output_tokens": resp.output_tokens,
            "latency_ms": resp.latency_ms,
            "cost_usd": resp.cost_usd,
            "output_digest": content_hash({"text": resp.text}),
            "output_preview": resp.text[:200],
            "prompt_digest": content_hash({"prompt": request.prompt}),
        }
        self._append(payload)

    def _record_failure(
        self, request: GenerateRequest, reason: str, *, structured: bool = False
    ) -> None:
        ref = getattr(self._inner, "model_ref", None)
        payload = {
            "status": "error",
            "mode": "structured" if structured else "generate",
            "provider": getattr(ref, "provider", "unknown"),
            "model": getattr(ref, "model", "unknown"),
            "version": getattr(ref, "version", "unknown"),
            "input_tokens": 0,
            "output_tokens": 0,
            "latency_ms": 0.0,
            "cost_usd": None,
            "error": reason[:500],
            "prompt_digest": content_hash({"prompt": request.prompt}),
        }
        self._append(payload)

    def _append(self, payload: dict[str, Any]) -> None:
        self.calls.append(payload)
        self._ledger.append(
            event_type="model.invoked",
            tenant_id=self._tenant_id,
            workspace_id=self._workspace_id,
            goal_id=self._goal_id,
            payload=payload,
            producer=self._producer,
        )
