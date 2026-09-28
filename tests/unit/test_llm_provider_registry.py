from personal_ai.core.llm import LLMProvider
from personal_ai.core.llm_config import validate_llm_provider_config
from personal_ai.core.llm_provider_registry import ProviderRegistry, ProviderSelection


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

def test_registry_selection_exposes_provider_boundary() -> None:
    config = validate_llm_provider_config(
        {
            "version": 2,
            "providers": {
                "my_llm": {
                    "enabled": True,
                    "type": "cloud",
                    "adapter": "openai_compatible",
                    "base_url": "https://example.invalid/v1",
                    "model": "example-model",
                    "api_key_env": "TEST_API_KEY",
                },
            },
        }
    )

    registry = ProviderRegistry(config)
    selection = registry.selection("my_llm")

    assert isinstance(selection, ProviderSelection)
    assert selection.provider_id == "my_llm"
    assert selection.adapter == "openai_compatible"
    assert selection.model == "example-model"


def test_registry_selection_for_fake_provider_has_no_model() -> None:
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
    selection = registry.selection("fake")

    assert selection.provider_id == "fake"
    assert selection.adapter == "fake"
    assert selection.model is None


def test_registry_selection_rejects_unknown_provider() -> None:
    import pytest

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

    with pytest.raises(ValueError, match="Unknown provider"):
        registry.selection("missing")


def test_registry_selection_rejects_disabled_provider() -> None:
    import pytest

    config = validate_llm_provider_config(
        {
            "version": 2,
            "providers": {
                "disabled": {
                    "enabled": False,
                    "type": "local",
                    "adapter": "fake",
                },
            },
        }
    )

    registry = ProviderRegistry(config)

    with pytest.raises(ValueError, match="Provider is disabled"):
        registry.selection("disabled")


def test_registry_create_still_returns_llm_provider() -> None:
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


def test_registry_selection_does_not_expose_credentials() -> None:
    config = validate_llm_provider_config(
        {
            "version": 2,
            "providers": {
                "my_llm": {
                    "enabled": True,
                    "type": "cloud",
                    "adapter": "openai_compatible",
                    "base_url": "https://example.invalid/v1",
                    "model": "example-model",
                    "api_key_env": "TEST_API_KEY",
                },
            },
        }
    )

    registry = ProviderRegistry(config)
    selection = registry.selection("my_llm")

    assert not hasattr(selection, "api_key")
    assert not hasattr(selection, "api_key_env")
    assert "TEST_API_KEY" not in repr(selection)

def test_registry_resolves_fake_adapter() -> None:
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

    assert registry.resolve_adapter("fake") == "fake"


def test_registry_resolves_openai_compatible_adapter() -> None:
    config = validate_llm_provider_config(
        {
            "version": 2,
            "providers": {
                "my_llm": {
                    "enabled": True,
                    "type": "cloud",
                    "adapter": "openai_compatible",
                    "base_url": "https://example.invalid/v1",
                    "model": "example-model",
                    "api_key_env": "TEST_API_KEY",
                },
            },
        }
    )

    registry = ProviderRegistry(config)

    assert registry.resolve_adapter("my_llm") == "openai_compatible"


def test_registry_resolve_adapter_rejects_unknown_provider() -> None:
    import pytest

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

    with pytest.raises(ValueError, match="Unknown provider"):
        registry.resolve_adapter("missing")


def test_registry_resolve_adapter_rejects_disabled_provider() -> None:
    import pytest

    config = validate_llm_provider_config(
        {
            "version": 2,
            "providers": {
                "disabled": {
                    "enabled": False,
                    "type": "local",
                    "adapter": "fake",
                },
            },
        }
    )

    registry = ProviderRegistry(config)

    with pytest.raises(ValueError, match="Provider is disabled"):
        registry.resolve_adapter("disabled")
