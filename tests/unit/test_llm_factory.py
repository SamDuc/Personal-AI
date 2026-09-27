import pytest

from personal_ai.core.llm import (
    ChatMessage,
    LLMProvider,
    LLMRequest,
    LLMResponse,
)
from personal_ai.core.llm_config import validate_llm_provider_config
from personal_ai.core.llm_factory import create_llm_provider


def test_create_provider_from_valid_enabled_config() -> None:
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

    provider = create_llm_provider(config, "fake")

    assert isinstance(provider, LLMProvider)


def test_disabled_provider_is_rejected() -> None:
    config = validate_llm_provider_config(
        {
            "version": 2,
            "providers": {
                "fake": {
                    "enabled": False,
                    "type": "local",
                        "adapter": "fake",
                },
            },
        }
    )

    with pytest.raises(ValueError):
        create_llm_provider(config, "fake")


def test_unknown_provider_is_rejected() -> None:
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

    with pytest.raises(ValueError):
        create_llm_provider(config, "unknown")


def test_factory_returns_llm_provider_interface() -> None:
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

    provider = create_llm_provider(config, "fake")

    assert isinstance(provider, LLMProvider)


def test_fake_provider_generates_llm_response() -> None:
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

    provider = create_llm_provider(config, "fake")

    response = provider.generate(
        LLMRequest(
            messages=[
                ChatMessage(role="user", content="Hello"),
            ],
        )
    )

    assert isinstance(response, LLMResponse)
    assert response.text
