import pytest

from personal_ai.core.llm_config import (
    LLMProviderConfig,
    validate_llm_provider_config,
)


def test_valid_provider_configuration() -> None:
    config = {
        "version": 2,
        "providers": {
            "example": {
                "enabled": False,
                "type": "cloud",
                "adapter": "fake",
            }
        },
    }

    result = validate_llm_provider_config(config)

    assert isinstance(result, LLMProviderConfig)
    assert result.version == 2
    assert result.providers["example"]["enabled"] is False
    assert result.providers["example"]["type"] == "cloud"


def test_missing_version_is_rejected() -> None:
    config = {
        "providers": {},
    }

    try:
        validate_llm_provider_config(config)
    except ValueError:
        pass
    else:
        raise AssertionError("Missing version must be rejected")


def test_invalid_provider_type_is_rejected() -> None:
    config = {
        "version": 2,
        "providers": {
            "example": {
                "enabled": False,
                "type": "invalid",
            }
        },
    }

    try:
        validate_llm_provider_config(config)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid provider type must be rejected")


def test_non_boolean_enabled_is_rejected() -> None:
    config = {
        "version": 2,
        "providers": {
            "example": {
                "enabled": "false",
                "type": "cloud",
                "adapter": "fake",
            }
        },
    }

    try:
        validate_llm_provider_config(config)
    except ValueError:
        pass
    else:
        raise AssertionError("Non-boolean enabled must be rejected")


def test_raw_api_key_is_rejected() -> None:
    config = {
        "version": 2,
        "providers": {
            "example": {
                "enabled": True,
                "type": "cloud",
                "adapter": "fake",
                "api_key": "secret-value",
            }
        },
    }

    try:
        validate_llm_provider_config(config)
    except ValueError:
        pass
    else:
        raise AssertionError("Raw API key must be rejected")


def test_raw_secret_is_rejected() -> None:
    config = {
        "version": 2,
        "providers": {
            "example": {
                "enabled": True,
                "type": "cloud",
                "adapter": "fake",
                "secret": "secret-value",
            }
        },
    }

    try:
        validate_llm_provider_config(config)
    except ValueError:
        pass
    else:
        raise AssertionError("Raw secret must be rejected")


def test_unknown_provider_field_is_rejected() -> None:
    config = {
        "version": 2,
        "providers": {
            "example": {
                "enabled": False,
                "type": "cloud",
                "adapter": "fake",
                "random_field": "unexpected",
            }
        },
    }

    try:
        validate_llm_provider_config(config)
    except ValueError:
        pass
    else:
        raise AssertionError("Unknown provider fields must be rejected")

def test_valid_openai_compatible_provider_configuration() -> None:
    config = {
        "version": 2,
        "providers": {
            "my_llm": {
                "enabled": False,
                "type": "cloud",
                "adapter": "openai_compatible",
                "base_url": "http://localhost:4000/v1",
                "model": "test-model",
                "api_key_env": "TEST_LLM_API_KEY",
            }
        },
    }

    result = validate_llm_provider_config(config)

    assert result.version == 2
    assert result.providers["my_llm"]["adapter"] == "openai_compatible"


def test_openai_compatible_requires_base_url() -> None:
    config = {
        "version": 2,
        "providers": {
            "my_llm": {
                "enabled": False,
                "type": "cloud",
                "adapter": "openai_compatible",
                "model": "test-model",
                "api_key_env": "TEST_LLM_API_KEY",
            }
        },
    }

    with pytest.raises(ValueError, match="base_url"):
        validate_llm_provider_config(config)


def test_openai_compatible_requires_model() -> None:
    config = {
        "version": 2,
        "providers": {
            "my_llm": {
                "enabled": False,
                "type": "cloud",
                "adapter": "openai_compatible",
                "base_url": "http://localhost:4000/v1",
                "api_key_env": "TEST_LLM_API_KEY",
            }
        },
    }

    with pytest.raises(ValueError, match="model"):
        validate_llm_provider_config(config)


def test_openai_compatible_allows_missing_api_key_env() -> None:
    config = {
        "version": 2,
        "providers": {
            "my_llm": {
                "enabled": True,
                "type": "local",
                "adapter": "openai_compatible",
                "base_url": "http://localhost:11434/v1",
                "model": "qwen2.5:3b",
            }
        },
    }

    result = validate_llm_provider_config(config)
    assert result.providers["my_llm"]["adapter"] == "openai_compatible"


def test_openai_compatible_rejects_empty_api_key_env() -> None:
    config = {
        "version": 2,
        "providers": {
            "my_llm": {
                "enabled": False,
                "type": "cloud",
                "adapter": "openai_compatible",
                "base_url": "https://example.invalid/v1",
                "model": "test-model",
                "api_key_env": "   ",
            }
        },
    }

    with pytest.raises(ValueError, match="api_key_env"):
        validate_llm_provider_config(config)


def test_unknown_adapter_is_rejected() -> None:
    config = {
        "version": 2,
        "providers": {
            "my_llm": {
                "enabled": False,
                "type": "cloud",
                "adapter": "unknown_adapter",
            }
        },
    }

    with pytest.raises(ValueError, match="Unsupported provider adapter"):
        validate_llm_provider_config(config)


@pytest.mark.parametrize(
    "base_url",
    [
        "http://example.com/v1",
        "https://localhost:11434/v1",
        "http://localhost.example/v1",
        "http://192.168.1.20:11434/v1",
        "http://user:pass@localhost:11434/v1",
    ],
)
def test_local_provider_rejects_non_loopback_url(base_url: str) -> None:
    config = {
        "version": 2,
        "providers": {
            "my_llm": {
                "enabled": True,
                "type": "local",
                "adapter": "openai_compatible",
                "base_url": base_url,
                "model": "test-model",
            }
        },
    }

    with pytest.raises(ValueError, match="loopback HTTP base_url"):
        validate_llm_provider_config(config)


@pytest.mark.parametrize(
    "base_url",
    [
        "http://localhost:11434/v1",
        "http://127.0.0.1:11434/v1",
        "http://[::1]:11434/v1",
    ],
)
def test_local_provider_accepts_loopback_url(base_url: str) -> None:
    config = {
        "version": 2,
        "providers": {
            "my_llm": {
                "enabled": True,
                "type": "local",
                "adapter": "openai_compatible",
                "base_url": base_url,
                "model": "test-model",
            }
        },
    }

    result = validate_llm_provider_config(config)
    assert result.providers["my_llm"]["base_url"] == base_url
