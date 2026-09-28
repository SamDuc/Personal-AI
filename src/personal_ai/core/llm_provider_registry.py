from dataclasses import dataclass

from personal_ai.core.llm import LLMProvider
from personal_ai.core.llm_config import LLMProviderConfig
from personal_ai.core.llm_factory import create_llm_provider


@dataclass(frozen=True)
class ProviderSelection:
    provider_id: str
    adapter: str
    model: str | None


@dataclass(frozen=True)
class ProviderProfile:
    provider_id: str
    provider_type: str
    adapter: str
    model: str | None


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

    def selection(self, provider_id: str) -> ProviderSelection:
        if provider_id not in self._config.providers:
            raise ValueError(f"Unknown provider: {provider_id}")

        provider_config = self._config.providers[provider_id]

        if not provider_config["enabled"]:
            raise ValueError(f"Provider is disabled: {provider_id}")

        return ProviderSelection(
            provider_id=provider_id,
            adapter=provider_config["adapter"],
            model=provider_config.get("model"),
        )

    def profile(self, provider_id: str) -> ProviderProfile:
        selection = self.selection(provider_id)
        provider_config = self._config.providers[provider_id]

        return ProviderProfile(
            provider_id=selection.provider_id,
            provider_type=provider_config["type"],
            adapter=selection.adapter,
            model=selection.model,
        )

    def resolve_adapter(self, provider_id: str) -> str:
        return self.selection(provider_id).adapter

    def create(self, provider_id: str) -> LLMProvider:
        self.selection(provider_id)
        return create_llm_provider(self._config, provider_id)