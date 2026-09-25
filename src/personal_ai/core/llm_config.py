from dataclasses import dataclass

SUPPORTED_PROVIDER_TYPES = {"cloud", "local"}
SUPPORTED_CONFIG_VERSION = 1
ALLOWED_PROVIDER_FIELDS = {"enabled", "type"}
FORBIDDEN_SECRET_FIELDS = {
    "api_key",
    "apikey",
    "secret",
    "secret_key",
    "password",
    "token",
    "access_token",
    "refresh_token",
    "credential",
    "credentials",
}


@dataclass(frozen=True)
class LLMProviderConfig:
    version: int
    providers: dict[str, dict[str, object]]


def validate_llm_provider_config(
    config: dict[str, object],
) -> LLMProviderConfig:
    if "version" not in config:
        raise ValueError("Missing required field: version")

    if config["version"] != SUPPORTED_CONFIG_VERSION:
        raise ValueError("Unsupported configuration version")

    if "providers" not in config:
        raise ValueError("Missing required field: providers")

    providers = config["providers"]

    if not isinstance(providers, dict):
        raise ValueError("providers must be a dictionary")

    validated_providers: dict[str, dict[str, object]] = {}

    for provider_id, provider_config in providers.items():
        if not isinstance(provider_id, str) or not provider_id:
            raise ValueError("Provider identifier must be a non-empty string")

        if not isinstance(provider_config, dict):
            raise ValueError(f"Invalid configuration for provider: {provider_id}")

        forbidden_fields = set(provider_config.keys()) & FORBIDDEN_SECRET_FIELDS
        if forbidden_fields:
            raise ValueError(
                f"Provider configuration contains forbidden secret fields: "
                f"{sorted(forbidden_fields)}"
            )

        unknown_fields = set(provider_config.keys()) - ALLOWED_PROVIDER_FIELDS
        if unknown_fields:
            raise ValueError(
                f"Provider configuration contains unknown fields: "
                f"{sorted(unknown_fields)}"
            )

        if "enabled" not in provider_config:
            raise ValueError(f"Missing enabled field for provider: {provider_id}")

        if not isinstance(provider_config["enabled"], bool):
            raise ValueError(f"enabled must be a boolean for provider: {provider_id}")

        if "type" not in provider_config:
            raise ValueError(f"Missing type field for provider: {provider_id}")

        provider_type = provider_config["type"]

        if provider_type not in SUPPORTED_PROVIDER_TYPES:
            raise ValueError(f"Unsupported provider type: {provider_type}")

        validated_providers[provider_id] = {
            "enabled": provider_config["enabled"],
            "type": provider_type,
        }

    return LLMProviderConfig(
        version=config["version"],
        providers=validated_providers,
    )
