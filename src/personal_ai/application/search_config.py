from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SearchConfig:
    enabled: bool = False
    provider: str = "tavily"
    api_key_env: str = "PERSONAL_AI_TAVILY_API_KEY"
    timeout_seconds: int = 10
    max_results: int = 5

    @classmethod
    def from_mapping(cls, config: object) -> SearchConfig:
        if not isinstance(config, dict):
            raise ValueError("search configuration must be a mapping.")

        enabled = config.get("enabled", False)
        provider = config.get("provider", "tavily")
        api_key_env = config.get("api_key_env", "PERSONAL_AI_TAVILY_API_KEY")
        timeout = config.get("timeout_seconds", 10)
        max_results = config.get("max_results", 5)

        if not isinstance(enabled, bool):
            raise ValueError("search.enabled must be a boolean.")
        if not isinstance(provider, str) or not provider.strip():
            raise ValueError("search.provider must be a non-empty string.")
        if not isinstance(api_key_env, str) or not re.fullmatch(
            r"[A-Za-z_][A-Za-z0-9_]*", api_key_env
        ):
            raise ValueError("search.api_key_env must be a valid environment variable name.")
        if isinstance(timeout, bool) or not isinstance(timeout, int) or not 1 <= timeout <= 60:
            raise ValueError("search.timeout_seconds must be an integer from 1 to 60.")
        if (
            isinstance(max_results, bool)
            or not isinstance(max_results, int)
            or not 1 <= max_results <= 10
        ):
            raise ValueError("search.max_results must be an integer from 1 to 10.")

        return cls(
            enabled=enabled,
            provider=provider.strip().lower(),
            api_key_env=api_key_env,
            timeout_seconds=timeout,
            max_results=max_results,
        )
