from personal_ai.core.llm_config import validate_llm_provider_config
from personal_ai.core.llm_execution_strategy import (
    ExecutionStrategyResolver,
    LLMExecutionStrategy,
)
from personal_ai.core.llm_provider_registry import ProviderRegistry
from personal_ai.core.llm_provider_resolver import ProviderResolver


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
                "openai_test": {
                    "enabled": True,
                    "type": "cloud",
                    "adapter": "openai_compatible",
                    "base_url": "https://example.invalid/v1",
                    "model": "test-model",
                    "api_key_env": "TEST_LLM_API_KEY",
                },
            },
        }
    )
    return ProviderRegistry(config)


def make_resolver() -> ExecutionStrategyResolver:
    return ExecutionStrategyResolver(
        ProviderResolver(make_registry())
    )


def test_fake_provider_resolves_to_fake_execution_strategy() -> None:
    resolver = make_resolver()

    strategy = resolver.resolve("fake")

    assert strategy == LLMExecutionStrategy.FAKE


def test_openai_compatible_provider_resolves_to_protocol_strategy() -> None:
    resolver = make_resolver()

    strategy = resolver.resolve("openai_test")

    assert strategy == LLMExecutionStrategy.OPENAI_COMPATIBLE


def test_execution_strategy_is_independent_of_provider_id() -> None:
    config = validate_llm_provider_config(
        {
            "version": 2,
            "providers": {
                "provider_a": {
                    "enabled": True,
                    "type": "cloud",
                    "adapter": "openai_compatible",
                    "base_url": "https://example.invalid/v1",
                    "model": "model-a",
                    "api_key_env": "TEST_LLM_API_KEY",
                },
                "provider_b": {
                    "enabled": True,
                    "type": "cloud",
                    "adapter": "openai_compatible",
                    "base_url": "https://example.invalid/v1",
                    "model": "model-b",
                    "api_key_env": "TEST_LLM_API_KEY",
                },
            },
        }
    )

    resolver = ExecutionStrategyResolver(
        ProviderResolver(ProviderRegistry(config))
    )

    assert resolver.resolve("provider_a") == LLMExecutionStrategy.OPENAI_COMPATIBLE
    assert resolver.resolve("provider_b") == LLMExecutionStrategy.OPENAI_COMPATIBLE
