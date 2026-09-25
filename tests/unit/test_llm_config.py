from personal_ai.core.llm_config import (
    LLMProviderConfig,
    validate_llm_provider_config,
)


def test_valid_provider_configuration() -> None:
    config = {
        "version": 1,
        "providers": {
            "example": {
                "enabled": False,
                "type": "cloud",
            }
        },
    }

    result = validate_llm_provider_config(config)

    assert isinstance(result, LLMProviderConfig)
    assert result.version == 1
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
        "version": 1,
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
        "version": 1,
        "providers": {
            "example": {
                "enabled": "false",
                "type": "cloud",
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
        "version": 1,
        "providers": {
            "example": {
                "enabled": True,
                "type": "cloud",
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
        "version": 1,
        "providers": {
            "example": {
                "enabled": True,
                "type": "cloud",
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
        "version": 1,
        "providers": {
            "example": {
                "enabled": False,
                "type": "cloud",
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
