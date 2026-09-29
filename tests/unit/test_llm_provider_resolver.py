import pytest

from personal_ai.core.llm import LLMProvider
from personal_ai.core.llm_config import validate_llm_provider_config
from personal_ai.core.llm_factory import FakeLLMProvider
from personal_ai.core.llm_provider_registry import ProviderRegistry
from personal_ai.core.llm_provider_resolver import (
    ProviderResolution,
    ProviderResolver,
)
from personal_ai.core.openai_compatible import OpenAICompatibleProvider


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
                "disabled": {
                    "enabled": False,
                    "type": "local",
                    "adapter": "fake",
                },
            },
        }
    )
    return ProviderRegistry(config)


def test_resolver_returns_provider_resolution() -> None:
    resolver = ProviderResolver(make_registry())

    result = resolver.resolve("fake")

    assert isinstance(result, ProviderResolution)
    assert result.provider_id == "fake"
    assert result.adapter == "fake"
    assert result.model is None
    assert isinstance(result.provider, LLMProvider)


def test_resolver_creates_fake_provider() -> None:
    resolver = ProviderResolver(make_registry())

    result = resolver.resolve("fake")

    assert isinstance(result.provider, FakeLLMProvider)


def test_resolver_creates_openai_compatible_provider() -> None:
    resolver = ProviderResolver(make_registry())

    result = resolver.resolve("openai_test")

    assert isinstance(result.provider, OpenAICompatibleProvider)
    assert result.provider_id == "openai_test"
    assert result.adapter == "openai_compatible"
    assert result.model == "test-model"


def test_resolver_matches_registry_adapter() -> None:
    registry = make_registry()
    resolver = ProviderResolver(registry)

    result = resolver.resolve("openai_test")

    assert result.adapter == registry.resolve_adapter("openai_test")


def test_resolver_matches_registry_profile() -> None:
    registry = make_registry()
    resolver = ProviderResolver(registry)

    profile = registry.profile("openai_test")
    result = resolver.resolve("openai_test")

    assert result.provider_id == profile.provider_id
    assert result.adapter == profile.adapter
    assert result.model == profile.model


def test_resolver_rejects_unknown_provider() -> None:
    resolver = ProviderResolver(make_registry())

    with pytest.raises(ValueError, match="Unknown provider"):
        resolver.resolve("unknown")


def test_resolver_rejects_disabled_provider() -> None:
    resolver = ProviderResolver(make_registry())

    with pytest.raises(ValueError, match="Provider is disabled"):
        resolver.resolve("disabled")


def test_resolution_contains_only_safe_provider_metadata() -> None:
    resolver = ProviderResolver(make_registry())

    result = resolver.resolve("openai_test")

    assert not hasattr(result, "api_key")
    assert not hasattr(result, "api_key_env")
    assert not hasattr(result, "secret")
    assert not hasattr(result, "credentials")
    assert "TEST_LLM_API_KEY" not in repr(result)


def test_resolution_does_not_mutate_registry() -> None:
    registry = make_registry()
    before = registry.profiles()

    ProviderResolver(registry).resolve("openai_test")

    after = registry.profiles()

    assert after == before


def test_resolution_is_provider_agnostic() -> None:
    resolver = ProviderResolver(make_registry())

    fake_result = resolver.resolve("fake")
    openai_result = resolver.resolve("openai_test")

    assert isinstance(fake_result.provider, LLMProvider)
    assert isinstance(openai_result.provider, LLMProvider)
    assert fake_result.adapter == "fake"
    assert openai_result.adapter == "openai_compatible"
