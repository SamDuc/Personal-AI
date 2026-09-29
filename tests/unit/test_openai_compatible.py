import json
from typing import Self

import pytest

from personal_ai.core.llm import ChatMessage, LLMRequest
from personal_ai.core.openai_compatible import OpenAICompatibleProvider


class FakeHTTPResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def read(self) -> bytes:
        return self._body


def test_generate_sends_openai_compatible_request() -> None:
    captured = {}

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        captured["method"] = req.method
        captured["body"] = json.loads(req.data.decode("utf-8"))
        captured["timeout"] = timeout
        return FakeHTTPResponse(
            b'{"choices":[{"message":{"content":"hello"}}]}'
        )

    provider = OpenAICompatibleProvider(
        base_url="http://localhost:8000/v1",
        model="test-model",
        timeout=12.5,
        urlopen=fake_urlopen,
    )

    response = provider.generate(
        LLMRequest(
            messages=[
                ChatMessage(role="user", content="Hello"),
            ]
        )
    )

    assert response.text == "hello"
    assert captured["url"] == "http://localhost:8000/v1/chat/completions"
    assert captured["method"] == "POST"
    assert captured["timeout"] == 12.5
    assert captured["body"] == {
        "model": "test-model",
        "messages": [
            {
                "role": "user",
                "content": "Hello",
            }
        ],
    }


def test_generate_uses_api_key_environment_variable(monkeypatch) -> None:
    captured = {}

    def fake_urlopen(req, timeout):
        captured["authorization"] = req.get_header("Authorization")
        return FakeHTTPResponse(
            b'{"choices":[{"message":{"content":"ok"}}]}'
        )

    monkeypatch.setenv("TEST_LLM_API_KEY", "secret-value")

    provider = OpenAICompatibleProvider(
        base_url="http://localhost:8000/v1",
        model="test-model",
        api_key_env="TEST_LLM_API_KEY",
        urlopen=fake_urlopen,
    )

    provider.generate(LLMRequest(messages=[]))

    assert captured["authorization"] == "Bearer secret-value"


def test_generate_rejects_missing_api_key(monkeypatch) -> None:
    monkeypatch.delenv("TEST_LLM_API_KEY", raising=False)

    provider = OpenAICompatibleProvider(
        base_url="http://localhost:8000/v1",
        model="test-model",
        api_key_env="TEST_LLM_API_KEY",
        urlopen=lambda *_args, **_kwargs: pytest.fail(
            "HTTP request must not run"
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="API key environment variable is not set",
    ):
        provider.generate(LLMRequest(messages=[]))


def test_generate_rejects_invalid_response() -> None:
    def fake_urlopen(req, timeout):
        return FakeHTTPResponse(b'{"unexpected": "response"}')

    provider = OpenAICompatibleProvider(
        base_url="http://localhost:8000/v1",
        model="test-model",
        urlopen=fake_urlopen,
    )

    with pytest.raises(RuntimeError, match="invalid response"):
        provider.generate(LLMRequest(messages=[]))


def test_generate_rejects_invalid_json() -> None:
    def fake_urlopen(req, timeout):
        return FakeHTTPResponse(b"not-json")

    provider = OpenAICompatibleProvider(
        base_url="http://localhost:8000/v1",
        model="test-model",
        urlopen=fake_urlopen,
    )

    with pytest.raises(RuntimeError, match="invalid JSON"):
        provider.generate(LLMRequest(messages=[]))


@pytest.mark.parametrize(
    ("base_url", "model"),
    [
        ("", "model"),
        ("   ", "model"),
        ("http://localhost", ""),
        ("http://localhost", "   "),
    ],
)
def test_invalid_configuration_is_rejected(
    base_url: str,
    model: str,
) -> None:
    with pytest.raises(ValueError):
        OpenAICompatibleProvider(
            base_url=base_url,
            model=model,
        )


def test_generate_rejects_empty_api_key(monkeypatch) -> None:
    monkeypatch.setenv("TEST_LLM_API_KEY", "")

    provider = OpenAICompatibleProvider(
        base_url="http://localhost:8000/v1",
        model="test-model",
        api_key_env="TEST_LLM_API_KEY",
        urlopen=lambda *_args, **_kwargs: pytest.fail(
            "HTTP request must not run"
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="API key environment variable is not set",
    ):
        provider.generate(LLMRequest(messages=[]))


def test_generate_reads_api_key_at_request_time(monkeypatch) -> None:
    captured = {}

    def fake_urlopen(req, timeout):
        captured["authorization"] = req.get_header("Authorization")
        return FakeHTTPResponse(
            b'{"choices":[{"message":{"content":"ok"}}]}'
        )

    monkeypatch.setenv("TEST_LLM_API_KEY", "first-key")

    provider = OpenAICompatibleProvider(
        base_url="http://localhost:8000/v1",
        model="test-model",
        api_key_env="TEST_LLM_API_KEY",
        urlopen=fake_urlopen,
    )

    monkeypatch.setenv("TEST_LLM_API_KEY", "second-key")

    provider.generate(LLMRequest(messages=[]))

    assert captured["authorization"] == "Bearer second-key"


def test_provider_does_not_store_api_key_value(monkeypatch) -> None:
    monkeypatch.setenv("TEST_LLM_API_KEY", "secret-value")

    provider = OpenAICompatibleProvider(
        base_url="http://localhost:8000/v1",
        model="test-model",
        api_key_env="TEST_LLM_API_KEY",
    )

    assert "secret-value" not in repr(provider.__dict__)
    assert provider.__dict__["_api_key_env"] == "TEST_LLM_API_KEY"


def test_missing_api_key_error_does_not_contain_secret(monkeypatch) -> None:
    monkeypatch.delenv("TEST_LLM_API_KEY", raising=False)

    provider = OpenAICompatibleProvider(
        base_url="http://localhost:8000/v1",
        model="test-model",
        api_key_env="TEST_LLM_API_KEY",
        urlopen=lambda *_args, **_kwargs: pytest.fail(
            "HTTP request must not run"
        ),
    )

    with pytest.raises(RuntimeError) as exc_info:
        provider.generate(LLMRequest(messages=[]))

    assert "TEST_LLM_API_KEY" in str(exc_info.value)
    assert "secret-value" not in str(exc_info.value)
