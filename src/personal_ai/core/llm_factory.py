from personal_ai.core.llm import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
)
from personal_ai.core.llm_config import LLMProviderConfig
from personal_ai.core.openai_compatible import OpenAICompatibleProvider


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

    adapter = provider_config["adapter"]

    if adapter == "fake":
        return FakeLLMProvider()

    if adapter == "openai_compatible":
        return OpenAICompatibleProvider(
            base_url=provider_config["base_url"],
            model=provider_config["model"],
            api_key_env=provider_config.get("api_key_env"),
        )

    raise ValueError(f"Unsupported provider adapter: {adapter}")
