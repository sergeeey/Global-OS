from global_os.adapters.models.anthropic import AnthropicProvider
from global_os.adapters.models.base import (
    EchoModelProvider,
    GenerateRequest,
    GenerateResponse,
    ModelProvider,
    ModelProviderError,
    ModelRef,
    OutageModelProvider,
    SlowModelProvider,
    SwappableModelProvider,
)
from global_os.adapters.models.factory import (
    free_live_ready,
    live_keys_present,
    open_model_provider,
    require_live_providers,
)
from global_os.adapters.models.free_catalog import (
    allow_provider_for_classification,
    register_free_models,
)
from global_os.adapters.models.gemini import GeminiProvider
from global_os.adapters.models.groq import GroqProvider
from global_os.adapters.models.openai_compat import OpenAICompatProvider
from global_os.adapters.models.openrouter import OpenRouterProvider
from global_os.adapters.models.recording import RecordingModelProvider
from global_os.adapters.models.zero_cost import (
    assert_zero_cost_allowed,
    prefer_free_descriptor,
    scientific_eval_mode,
    zero_cost_mode_enabled,
)

__all__ = [
    "AnthropicProvider",
    "EchoModelProvider",
    "GeminiProvider",
    "GenerateRequest",
    "GenerateResponse",
    "GroqProvider",
    "ModelProvider",
    "ModelProviderError",
    "ModelRef",
    "OpenAICompatProvider",
    "OpenRouterProvider",
    "OutageModelProvider",
    "RecordingModelProvider",
    "SlowModelProvider",
    "SwappableModelProvider",
    "allow_provider_for_classification",
    "assert_zero_cost_allowed",
    "free_live_ready",
    "live_keys_present",
    "open_model_provider",
    "prefer_free_descriptor",
    "register_free_models",
    "require_live_providers",
    "scientific_eval_mode",
    "zero_cost_mode_enabled",
]
