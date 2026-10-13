from __future__ import annotations

import json
import os
from typing import Protocol

from personal_ai.application.search_config import SearchConfig
from personal_ai.tools.web_common import post_json, validate_public_https_url


class SearchProvider(Protocol):
    """Provider-neutral interface for public web search."""

    def search(self, query: str, max_results: int) -> list[dict[str, str]]:
        """Return normalized title/URL results or raise a clear error."""
        ...


class DisabledSearchProvider:
    def search(self, query: str, max_results: int) -> list[dict[str, str]]:
        raise RuntimeError("Web search is disabled in config/search.yaml.")


class TavilySearchProvider:
    """Official Tavily Search API adapter. The API key is never stored in config."""

    ENDPOINT = "https://api.tavily.com/search"

    def __init__(self, api_key_env: str, timeout_seconds: int = 10) -> None:
        self.api_key_env = api_key_env
        self.timeout_seconds = timeout_seconds

    def search(self, query: str, max_results: int) -> list[dict[str, str]]:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string.")
        query = query.strip()
        if len(query) > 500:
            raise ValueError("query is too long.")
        if (
            isinstance(max_results, bool)
            or not isinstance(max_results, int)
            or not 1 <= max_results <= 10
        ):
            raise ValueError("max_results must be an integer from 1 to 10.")

        api_key = os.environ.get(self.api_key_env)
        if not api_key or not api_key.strip():
            raise RuntimeError(
                f"Missing API key environment variable: {self.api_key_env}"
            )

        try:
            body = post_json(
                self.ENDPOINT,
                {
                    "api_key": api_key,
                    "query": query,
                    "search_depth": "basic",
                    "max_results": max_results,
                },
                timeout_seconds=self.timeout_seconds,
            )
        except RuntimeError:
            # Keep transport exception details, which may contain secrets, private.
            raise RuntimeError("Search provider request failed.") from None
        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("Search provider returned invalid JSON.") from exc

        if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
            raise RuntimeError("Search provider response has an invalid schema.")

        normalized: list[dict[str, str]] = []
        for item in payload["results"]:
            if not isinstance(item, dict):
                continue
            title = item.get("title")
            url = item.get("url")
            if not isinstance(title, str) or not title.strip():
                continue
            if not isinstance(url, str) or not url.strip():
                continue
            try:
                safe_url = validate_public_https_url(url)
            except ValueError:
                # Ignore malformed, non-HTTPS, or non-public result URLs.
                continue
            normalized.append({"title": title.strip()[:500], "url": safe_url})
            if len(normalized) >= max_results:
                break
        return normalized


def build_search_provider(config: SearchConfig) -> SearchProvider:
    if not config.enabled:
        return DisabledSearchProvider()
    if config.provider == "tavily":
        return TavilySearchProvider(
            api_key_env=config.api_key_env,
            timeout_seconds=config.timeout_seconds,
        )
    raise ValueError(f"Unsupported search provider: {config.provider}")
