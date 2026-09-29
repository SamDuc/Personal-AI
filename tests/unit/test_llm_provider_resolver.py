import pytest

from personal_ai.core.llm import LLMProvider
from personal_ai.core.llm_config import validate_llm_provider_config
from personal_ai.core.llm_factory import FakeLLMProvider
from personal_ai.core.llm_provider_registry import ProviderRegistry
from personal_ai.core.llm_provider_resolver import (
    ProviderResolution,
    ProviderResolver,
)


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

    result = resolver.resolve("fake")

    assert not hasattr(result, "api_key")
    assert not hasattr(result, "api_key_env")
    assert not hasattr(result, "secret")
    assert not hasattr(result, "credentials")


def test_resolution_does_not_mutate_registry() -> None:
    registry = make_registry()
    before = registry.profiles()

    ProviderResolver(registry).resolve("fake")

    after = registry.profiles()

    assert after == before


def test_resolution_is_provider_agnostic() -> None:
    resolver = ProviderResolver(make_registry())

    result = resolver.resolve("fake")

    assert result.adapter == "fake"
    assert isinstance(result.provider, LLMProvider)
