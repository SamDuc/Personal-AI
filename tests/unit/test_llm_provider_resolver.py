import pytest

from personal_ai.core.llm import LLMProvider
from personal_ai.core.llm_config import validate_llm_provider_config
from personal_ai.core.llm_factory import (
    FakeLLMProvider,
    create_llm_provider,
)
from personal_ai.core.llm_provider_registry import ProviderRegistry
from personal_ai.core.llm_provider_resolver import ProviderResolver
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


def test_resolver_factory_integration_for_fake() -> None:
    registry = make_registry()
    resolver = ProviderResolver(registry)

    resolved = resolver.resolve("fake")
    direct = create_llm_provider(registry._config, "fake")

    assert isinstance(resolved.provider, FakeLLMProvider)
    assert isinstance(direct, FakeLLMProvider)
    assert type(resolved.provider) is type(direct)


def test_resolver_factory_integration_for_openai_compatible() -> None:
    registry = make_registry()
    resolver = ProviderResolver(registry)

    resolved = resolver.resolve("openai_test")
    direct = create_llm_provider(registry._config, "openai_test")

    assert isinstance(resolved.provider, OpenAICompatibleProvider)
    assert isinstance(direct, OpenAICompatibleProvider)
    assert type(resolved.provider) is type(direct)
    assert resolved.adapter == "openai_compatible"
    assert resolved.model == "test-model"


def test_resolver_does_not_require_api_key_during_resolution(
    monkeypatch,
) -> None:
    monkeypatch.delenv("TEST_LLM_API_KEY", raising=False)

    registry = make_registry()
    result = ProviderResolver(registry).resolve("openai_test")

    assert isinstance(result.provider, LLMProvider)


def test_factory_remains_independently_usable() -> None:
    registry = make_registry()

    provider = create_llm_provider(registry._config, "fake")

    assert isinstance(provider, FakeLLMProvider)


def test_resolver_preserves_factory_error_boundary() -> None:
    registry = make_registry()

    with pytest.raises(ValueError, match="Unknown provider"):
        ProviderResolver(registry).resolve("missing")
