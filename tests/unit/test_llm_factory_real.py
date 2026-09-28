import pytest

from personal_ai.core.llm_config import LLMProviderConfig
from personal_ai.core.llm_factory import (
    FakeLLMProvider,
    create_llm_provider,
)
from personal_ai.core.openai_compatible import OpenAICompatibleProvider


def test_factory_creates_fake_provider_from_fake_adapter() -> None:
    config = LLMProviderConfig(
        version=2,
        providers={
            "fake": {
                "enabled": True,
                "type": "local",
                "adapter": "fake",
            }
        },
    )

    provider = create_llm_provider(config, "fake")

    assert isinstance(provider, FakeLLMProvider)


def test_factory_creates_openai_compatible_provider() -> None:
    config = LLMProviderConfig(
        version=2,
        providers={
            "my_llm": {
                "enabled": True,
                "type": "cloud",
                "adapter": "openai_compatible",
                "base_url": "http://localhost:8000/v1",
                "model": "test-model",
                "api_key_env": "TEST_LLM_API_KEY",
            }
        },
    )

    provider = create_llm_provider(config, "my_llm")

    assert isinstance(provider, OpenAICompatibleProvider)


def test_factory_rejects_disabled_provider() -> None:
    config = LLMProviderConfig(
        version=2,
        providers={
            "my_llm": {
                "enabled": False,
                "type": "cloud",
                "adapter": "openai_compatible",
                "base_url": "http://localhost:8000/v1",
                "model": "test-model",
                "api_key_env": "TEST_LLM_API_KEY",
            }
        },
    )

    with pytest.raises(ValueError, match="Provider is disabled"):
        create_llm_provider(config, "my_llm")


def test_factory_rejects_unknown_adapter() -> None:
    config = LLMProviderConfig(
        version=2,
        providers={
            "custom": {
                "enabled": True,
                "type": "local",
                "adapter": "unknown",
            }
        },
    )

    with pytest.raises(ValueError, match="Unsupported provider adapter"):
        create_llm_provider(config, "custom")
