from personal_ai.core.llm_capability import LLMCapability
from personal_ai.core.llm_capability_resolver import CapabilityResolver
from personal_ai.core.llm_config import validate_llm_provider_config
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


def test_capability_resolver_returns_provider_capabilities() -> None:
    resolver = CapabilityResolver(
        ProviderResolver(make_registry())
    )

    capabilities = resolver.resolve("fake")

    assert capabilities.supports(LLMCapability.TEXT_INPUT)
    assert capabilities.supports(LLMCapability.TEXT_OUTPUT)


def test_capability_resolver_requires_supported_capability() -> None:
    resolver = CapabilityResolver(
        ProviderResolver(make_registry())
    )

    assert resolver.supports("fake", LLMCapability.TEXT_INPUT)
    assert resolver.supports("fake", LLMCapability.TEXT_OUTPUT)


def test_capability_resolver_rejects_unsupported_capability() -> None:
    resolver = CapabilityResolver(
        ProviderResolver(make_registry())
    )

    unsupported = object()

    assert not resolver.supports("fake", unsupported)  # type: ignore[arg-type]
