from personal_ai.core.llm import LLMProvider
from personal_ai.core.llm_config import LLMProviderConfig
from personal_ai.core.llm_factory import create_llm_provider


class ProviderRegistry:
    def __init__(self, config: LLMProviderConfig) -> None:
        self._config = config

    @property
    def provider_ids(self) -> tuple[str, ...]:
        return tuple(
            provider_id
            for provider_id, provider_config in self._config.providers.items()
            if provider_config["enabled"]
        )

    def create(self, provider_id: str) -> LLMProvider:
        if provider_id not in self._config.providers:
            raise ValueError(f"Unknown provider: {provider_id}")

        if not self._config.providers[provider_id]["enabled"]:
            raise ValueError(f"Provider is disabled: {provider_id}")

        return create_llm_provider(self._config, provider_id)
