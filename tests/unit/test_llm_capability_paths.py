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


def make_capability_resolver() -> CapabilityResolver:
    return CapabilityResolver(
        ProviderResolver(make_registry())
    )


def test_offline_fake_provider_exposes_text_capabilities() -> None:
    resolver = make_capability_resolver()

    assert resolver.supports("fake", LLMCapability.TEXT_INPUT)
    assert resolver.supports("fake", LLMCapability.TEXT_OUTPUT)


def test_online_openai_compatible_provider_exposes_text_capabilities() -> None:
    resolver = make_capability_resolver()

    assert resolver.supports("openai_test", LLMCapability.TEXT_INPUT)
    assert resolver.supports("openai_test", LLMCapability.TEXT_OUTPUT)


def test_offline_and_online_paths_share_the_same_capability_contract() -> None:
    resolver = make_capability_resolver()

    offline = resolver.resolve("fake")
    online = resolver.resolve("openai_test")

    assert offline.capabilities == online.capabilities
