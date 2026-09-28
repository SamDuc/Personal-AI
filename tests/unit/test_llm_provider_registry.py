from personal_ai.core.llm import LLMProvider
from personal_ai.core.llm_config import validate_llm_provider_config
from personal_ai.core.llm_provider_registry import ProviderRegistry


def test_registry_lists_enabled_providers_only() -> None:
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

    registry = ProviderRegistry(config)

    assert registry.provider_ids == ("fake",)


def test_registry_creates_enabled_provider() -> None:
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

    registry = ProviderRegistry(config)

    provider = registry.create("fake")

    assert isinstance(provider, LLMProvider)


def test_registry_rejects_unknown_provider() -> None:
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

    registry = ProviderRegistry(config)

    import pytest

    with pytest.raises(ValueError, match="Unknown provider"):
        registry.create("missing")


def test_registry_rejects_disabled_provider() -> None:
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

    registry = ProviderRegistry(config)

    import pytest

    with pytest.raises(ValueError, match="Provider is disabled"):
        registry.create("fake")


def test_registry_does_not_mutate_provider_configuration() -> None:
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

    before = dict(config.providers["fake"])

    registry = ProviderRegistry(config)
    registry.create("fake")

    assert config.providers["fake"] == before


def test_registry_does_not_expose_secret_values() -> None:
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

    registry = ProviderRegistry(config)

    assert "api_key" not in registry.__dict__
    assert "secret" not in registry.__dict__
    assert "token" not in registry.__dict__
