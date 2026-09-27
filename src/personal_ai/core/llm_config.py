from dataclasses import dataclass

SUPPORTED_CONFIG_VERSION = 2
SUPPORTED_PROVIDER_TYPES = {"cloud", "local"}
SUPPORTED_ADAPTERS = {"fake", "openai_compatible"}

ALLOWED_PROVIDER_FIELDS = {
    "enabled",
    "type",
    "adapter",
    "base_url",
    "model",
    "api_key_env",
}

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
            raise ValueError(
                f"Invalid configuration for provider: {provider_id}"
            )

        forbidden_fields = set(provider_config.keys()) & FORBIDDEN_SECRET_FIELDS
        if forbidden_fields:
            raise ValueError(
                "Provider configuration contains forbidden secret fields: "
                f"{sorted(forbidden_fields)}"
            )

        unknown_fields = set(provider_config.keys()) - ALLOWED_PROVIDER_FIELDS
        if unknown_fields:
            raise ValueError(
                "Provider configuration contains unknown fields: "
                f"{sorted(unknown_fields)}"
            )

        if "enabled" not in provider_config:
            raise ValueError(f"Missing enabled field for provider: {provider_id}")

        if not isinstance(provider_config["enabled"], bool):
            raise ValueError(
                f"enabled must be a boolean for provider: {provider_id}"
            )

        if "type" not in provider_config:
            raise ValueError(f"Missing type field for provider: {provider_id}")

        provider_type = provider_config["type"]

        if provider_type not in SUPPORTED_PROVIDER_TYPES:
            raise ValueError(f"Unsupported provider type: {provider_type}")

        adapter = provider_config.get("adapter")

        if not isinstance(adapter, str) or not adapter:
            raise ValueError(
                f"Missing or invalid adapter for provider: {provider_id}"
            )

        if adapter not in SUPPORTED_ADAPTERS:
            raise ValueError(f"Unsupported provider adapter: {adapter}")

        if adapter == "openai_compatible":
            base_url = provider_config.get("base_url")
            model = provider_config.get("model")
            api_key_env = provider_config.get("api_key_env")

            if not isinstance(base_url, str) or not base_url.strip():
                raise ValueError(
                    f"base_url must be a non-empty string for provider: "
                    f"{provider_id}"
                )

            if not isinstance(model, str) or not model.strip():
                raise ValueError(
                    f"model must be a non-empty string for provider: "
                    f"{provider_id}"
                )

            if not isinstance(api_key_env, str) or not api_key_env.strip():
                raise ValueError(
                    f"api_key_env must be a non-empty string for provider: "
                    f"{provider_id}"
                )

        validated_providers[provider_id] = dict(provider_config)

    return LLMProviderConfig(
        version=config["version"],
        providers=validated_providers,
    )
