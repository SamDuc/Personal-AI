from __future__ import annotations

import json

import pytest

from personal_ai.application.search_config import SearchConfig
from personal_ai.tools.search_providers import (
    DisabledSearchProvider,
    TavilySearchProvider,
    build_search_provider,
)


def test_search_config_defaults_to_disabled() -> None:
    config = SearchConfig.from_mapping({})
    assert config.enabled is False
    assert config.provider == "tavily"
    assert config.api_key_env == "PERSONAL_AI_TAVILY_API_KEY"


@pytest.mark.parametrize(
    "mapping",
    [
        {"enabled": "yes"},
        {"timeout_seconds": 0},
        {"timeout_seconds": 61},
        {"max_results": 0},
        {"max_results": 11},
        {"api_key_env": "not a valid env name"},
    ],
)
def test_search_config_rejects_invalid_values(mapping: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        SearchConfig.from_mapping(mapping)


def test_disabled_search_provider_is_fail_closed() -> None:
    provider = build_search_provider(SearchConfig())
    assert isinstance(provider, DisabledSearchProvider)
    with pytest.raises(RuntimeError, match="disabled"):
        provider.search("example query", 5)


def test_tavily_provider_requires_environment_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PERSONAL_AI_TEST_TAVILY_KEY", raising=False)
    provider = TavilySearchProvider("PERSONAL_AI_TEST_TAVILY_KEY")
    with pytest.raises(RuntimeError, match="PERSONAL_AI_TEST_TAVILY_KEY"):
        provider.search("example query", 5)


def test_tavily_provider_normalizes_results(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PERSONAL_AI_TEST_TAVILY_KEY", "test-only-key")
    monkeypatch.setattr(
        "personal_ai.tools.search_providers.post_json",
        lambda url, payload, timeout_seconds: json.dumps(
            {
                "results": [
                    {"title": "Example", "url": "https://example.com/"},
                    {"title": "", "url": "https://example.org/"},
                    {"title": "Unsafe", "url": "http://127.0.0.1/"},
                ]
            }
        ).encode("utf-8"),
    )
    monkeypatch.setattr(
        "personal_ai.tools.search_providers.validate_public_https_url",
        lambda url: url if url.startswith("https://") and "127.0.0.1" not in url else _raise_value_error(),
    )

    result = TavilySearchProvider("PERSONAL_AI_TEST_TAVILY_KEY").search(
        "example query", 5
    )
    assert result == [{"title": "Example", "url": "https://example.com/"}]


def _raise_value_error() -> str:
    raise ValueError("unsafe URL")


def test_search_provider_rejects_unknown_provider() -> None:
    config = SearchConfig.from_mapping({"enabled": True, "provider": "unknown"})
    with pytest.raises(ValueError, match="Unsupported search provider"):
        build_search_provider(config)


@pytest.mark.parametrize(
    ("query", "max_results"),
    [
        ("", 5),
        ("   ", 5),
        ("x" * 501, 5),
        ("valid query", 0),
        ("valid query", 11),
        ("valid query", True),
        ("valid query", False),
        (None, 5),
    ],
)
def test_tavily_provider_validates_input_before_network(
    monkeypatch: pytest.MonkeyPatch,
    query: object,
    max_results: object,
) -> None:
    monkeypatch.setenv("PERSONAL_AI_TEST_TAVILY_KEY", "test-only-key")

    def unexpected_request(*args, **kwargs):
        raise AssertionError("Invalid input must not reach the network.")

    monkeypatch.setattr(
        "personal_ai.tools.search_providers.post_json",
        unexpected_request,
    )

    provider = TavilySearchProvider("PERSONAL_AI_TEST_TAVILY_KEY")
    with pytest.raises(ValueError):
        provider.search(query, max_results)


def test_tavily_provider_passes_configured_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PERSONAL_AI_TEST_TAVILY_KEY", "test-only-key")
    captured = {}

    def fake_post_json(url, payload, *, timeout_seconds):
        captured["url"] = url
        captured["payload"] = payload
        captured["timeout_seconds"] = timeout_seconds
        return b'{"results": []}'

    monkeypatch.setattr(
        "personal_ai.tools.search_providers.post_json",
        fake_post_json,
    )

    provider = TavilySearchProvider(
        "PERSONAL_AI_TEST_TAVILY_KEY",
        timeout_seconds=7,
    )
    result = provider.search("example query", 3)

    assert result == []
    assert captured["url"] == "https://api.tavily.com/search"
    assert captured["timeout_seconds"] == 7
    assert captured["payload"]["api_key"] == "test-only-key"
    assert captured["payload"]["max_results"] == 3


@pytest.mark.parametrize(
    ("response_body", "expected_message"),
    [
        (b"not valid json", "invalid JSON"),
        (b'{"results": {}}', "invalid schema"),
    ],
)
def test_tavily_provider_rejects_malformed_responses(
    monkeypatch: pytest.MonkeyPatch,
    response_body: bytes,
    expected_message: str,
) -> None:
    monkeypatch.setenv("PERSONAL_AI_TEST_TAVILY_KEY", "test-only-key")
    monkeypatch.setattr(
        "personal_ai.tools.search_providers.post_json",
        lambda *args, **kwargs: response_body,
    )

    provider = TavilySearchProvider("PERSONAL_AI_TEST_TAVILY_KEY")
    with pytest.raises(RuntimeError, match=expected_message):
        provider.search("example query", 5)


def test_tavily_provider_does_not_expose_key_in_transport_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "distinctive-test-secret-123"
    monkeypatch.setenv("PERSONAL_AI_TEST_TAVILY_KEY", secret)

    def failing_request(*args, **kwargs):
        raise RuntimeError(f"Transport failed; token={secret}")

    monkeypatch.setattr(
        "personal_ai.tools.search_providers.post_json",
        failing_request,
    )

    provider = TavilySearchProvider("PERSONAL_AI_TEST_TAVILY_KEY")
    with pytest.raises(RuntimeError) as exc_info:
        provider.search("example query", 5)

    assert str(exc_info.value) == "Search provider request failed."
    assert secret not in str(exc_info.value)


def test_tavily_uses_real_url_validator_for_results(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PERSONAL_AI_TEST_TAVILY_KEY", "test-only-key")

    # Public literal IP avoids DNS/network access during URL validation.
    response = {
        "results": [
            {"title": "Public", "url": "https://1.1.1.1/"},
            {"title": "Loopback", "url": "https://127.0.0.1/"},
            {"title": "Private network", "url": "https://10.0.0.5/"},
        ]
    }
    monkeypatch.setattr(
        "personal_ai.tools.search_providers.post_json",
        lambda *args, **kwargs: json.dumps(response).encode("utf-8"),
    )

    # Intentionally do not mock validate_public_https_url.
    result = TavilySearchProvider("PERSONAL_AI_TEST_TAVILY_KEY").search(
        "example query", 5
    )

    assert result == [{"title": "Public", "url": "https://1.1.1.1/"}]
