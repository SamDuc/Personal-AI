from enum import Enum

from personal_ai.core.llm_provider_resolver import ProviderResolver


class LLMExecutionStrategy(str, Enum):
    FAKE = "fake"
    OPENAI_COMPATIBLE = "openai_compatible"


class ExecutionStrategyResolver:
    def __init__(self, provider_resolver: ProviderResolver) -> None:
        self._provider_resolver = provider_resolver

    def resolve(self, provider_id: str) -> LLMExecutionStrategy:
        resolution = self._provider_resolver.resolve(provider_id)

        try:
            return LLMExecutionStrategy(resolution.adapter)
        except ValueError as exc:
            raise ValueError(
                f"Unsupported execution adapter: {resolution.adapter}"
            ) from exc
