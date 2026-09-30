from personal_ai.core.llm_capability import LLMCapability, LLMCapabilitySet
from personal_ai.core.llm_provider_resolver import ProviderResolver


class CapabilityResolver:
    def __init__(self, provider_resolver: ProviderResolver) -> None:
        self._provider_resolver = provider_resolver

    def resolve(self, provider_id: str) -> LLMCapabilitySet:
        return self._provider_resolver.resolve(provider_id).capabilities

    def supports(self, provider_id: str, capability: LLMCapability) -> bool:
        if not isinstance(capability, LLMCapability):
            return False
        return self.resolve(provider_id).supports(capability)
