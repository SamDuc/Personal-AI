from dataclasses import dataclass

from personal_ai.core.llm import LLMProvider
from personal_ai.core.llm_provider_registry import ProviderProfile, ProviderRegistry


@dataclass(frozen=True)
class ProviderResolution:
    provider_id: str
    adapter: str
    model: str | None
    provider: LLMProvider


class ProviderResolver:
    def __init__(self, registry: ProviderRegistry) -> None:
        self._registry = registry

    def resolve(self, provider_id: str) -> ProviderResolution:
        profile: ProviderProfile = self._registry.profile(provider_id)
        provider = self._registry.create(provider_id)

        return ProviderResolution(
            provider_id=profile.provider_id,
            adapter=profile.adapter,
            model=profile.model,
            provider=provider,
        )
