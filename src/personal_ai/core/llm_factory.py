from personal_ai.core.llm import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
)
from personal_ai.core.llm_config import LLMProviderConfig


class FakeLLMProvider(LLMProvider):
    def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(text="fake response")


def create_llm_provider(
    config: LLMProviderConfig,
    provider_id: str,
) -> LLMProvider:
    if provider_id not in config.providers:
        raise ValueError(f"Unknown provider: {provider_id}")

    provider_config = config.providers[provider_id]

    if not provider_config["enabled"]:
        raise ValueError(f"Provider is disabled: {provider_id}")

    if provider_id != "fake":
        raise ValueError(f"Unsupported provider adapter: {provider_id}")

    return FakeLLMProvider()
