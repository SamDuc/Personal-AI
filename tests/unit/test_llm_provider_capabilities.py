from personal_ai.core.llm_capability import (
    LLMCapability,
    LLMCapabilitySet,
)
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


def test_fake_provider_profile_exposes_text_capabilities() -> None:
    profile = make_registry().profile("fake")

    assert isinstance(profile.capabilities, LLMCapabilitySet)
    assert profile.capabilities.supports(LLMCapability.TEXT_INPUT)
    assert profile.capabilities.supports(LLMCapability.TEXT_OUTPUT)


def test_openai_compatible_profile_exposes_text_capabilities() -> None:
    profile = make_registry().profile("openai_test")

    assert isinstance(profile.capabilities, LLMCapabilitySet)
    assert profile.capabilities.supports(LLMCapability.TEXT_INPUT)
    assert profile.capabilities.supports(LLMCapability.TEXT_OUTPUT)


def test_provider_resolution_preserves_capabilities() -> None:
    resolved = ProviderResolver(make_registry()).resolve("fake")

    assert isinstance(resolved.capabilities, LLMCapabilitySet)
    assert resolved.capabilities.supports(LLMCapability.TEXT_INPUT)
    assert resolved.capabilities.supports(LLMCapability.TEXT_OUTPUT)


def test_capability_metadata_is_immutable() -> None:
    profile = make_registry().profile("fake")

    assert isinstance(profile.capabilities.capabilities, frozenset)
