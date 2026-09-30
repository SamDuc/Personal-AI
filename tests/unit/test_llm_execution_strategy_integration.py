from personal_ai.core.llm import ChatMessage, LLMRequest
from personal_ai.core.llm_config import validate_llm_provider_config
from personal_ai.core.llm_execution_strategy import (
    ExecutionStrategyResolver,
    LLMExecutionStrategy,
)
from personal_ai.core.llm_provider_registry import ProviderRegistry
from personal_ai.core.llm_provider_resolver import ProviderResolver
from personal_ai.core.llm_runtime import LLMRuntime


def make_registry() -> ProviderRegistry:
    config = validate_llm_provider_config(
        {
            "version": 2,
            "providers": {
                "fake": {
                    "enabled": True,
                    "type": "local",
                    "adapter": "fake",
                },
            },
        }
    )
    return ProviderRegistry(config)


def test_execution_strategy_resolves_before_runtime_execution() -> None:
    provider_resolver = ProviderResolver(make_registry())
    strategy_resolver = ExecutionStrategyResolver(provider_resolver)

    strategy = strategy_resolver.resolve("fake")
    resolution = provider_resolver.resolve("fake")

    assert strategy is LLMExecutionStrategy.FAKE

    runtime = LLMRuntime(resolution.provider)
    response = runtime.generate(
        LLMRequest(
            messages=[
                ChatMessage(
                    role="user",
                    content="hello",
                )
            ]
        )
    )

    assert isinstance(response.text, str)
    assert response.text
