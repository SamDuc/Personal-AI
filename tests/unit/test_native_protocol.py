import json

import pytest

from personal_ai.core.llm import ChatMessage, LLMRequest
from personal_ai.core.openai_compatible import OpenAICompatibleProvider


class FakeHTTPResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None

    def read(self) -> bytes:
        return self._body


def test_native_protocol_contract_request_shape() -> None:
    captured = {}

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        captured["method"] = req.method
        captured["headers"] = dict(req.headers)
        captured["body"] = json.loads(req.data.decode("utf-8"))
        captured["timeout"] = timeout

        return FakeHTTPResponse(
            b'{"choices":[{"message":{"content":"ok"}}]}'
        )

    provider = OpenAICompatibleProvider(
        base_url="http://localhost:8000/v1",
        model="test-model",
        timeout=15.0,
        urlopen=fake_urlopen,
    )

    response = provider.generate(
        LLMRequest(
            messages=[
                ChatMessage(role="system", content="system"),
                ChatMessage(role="user", content="hello"),
            ]
        )
    )

    assert response.text == "ok"
    assert captured["url"] == (
        "http://localhost:8000/v1/chat/completions"
    )
    assert captured["method"] == "POST"
    assert captured["headers"]["Content-type"] == "application/json"
    assert captured["body"] == {
        "model": "test-model",
        "messages": [
            {"role": "system", "content": "system"},
            {"role": "user", "content": "hello"},
        ],
    }
    assert captured["timeout"] == 15.0


def test_native_protocol_contract_reads_api_key_at_request_time(
    monkeypatch,
) -> None:
    captured = {}

    def fake_urlopen(req, timeout):
        captured["authorization"] = req.get_header("Authorization")
        return FakeHTTPResponse(
            b'{"choices":[{"message":{"content":"ok"}}]}'
        )

    monkeypatch.setenv("TEST_NATIVE_PROTOCOL_KEY", "first-key")

    provider = OpenAICompatibleProvider(
        base_url="http://localhost:8000/v1",
        model="test-model",
        api_key_env="TEST_NATIVE_PROTOCOL_KEY",
        urlopen=fake_urlopen,
    )

    monkeypatch.setenv("TEST_NATIVE_PROTOCOL_KEY", "second-key")

    provider.generate(LLMRequest(messages=[]))

    assert captured["authorization"] == "Bearer second-key"


def test_native_protocol_contract_preserves_response_text() -> None:
    def fake_urlopen(req, timeout):
        return FakeHTTPResponse(
            b'{"choices":[{"message":{"content":"  hello\\nworld  "}}]}'
        )

    provider = OpenAICompatibleProvider(
        base_url="http://localhost:8000/v1",
        model="test-model",
        urlopen=fake_urlopen,
    )

    response = provider.generate(LLMRequest(messages=[]))

    assert response.text == "  hello\nworld  "


@pytest.mark.parametrize(
    ("body", "message"),
    [
        (b"not-json", "invalid JSON"),
        (b'{"unexpected":"response"}', "invalid response"),
        (
            b'{"choices":[{"message":{"content":{"text":"hello"}}}]}',
            "response content must be text",
        ),
    ],
)
def test_native_protocol_contract_rejects_invalid_responses(
    body: bytes,
    message: str,
) -> None:
    def fake_urlopen(req, timeout):
        return FakeHTTPResponse(body)

    provider = OpenAICompatibleProvider(
        base_url="http://localhost:8000/v1",
        model="test-model",
        urlopen=fake_urlopen,
    )

    with pytest.raises(RuntimeError, match=message):
        provider.generate(LLMRequest(messages=[]))


def test_native_protocol_contract_rejects_missing_api_key(
    monkeypatch,
) -> None:
    monkeypatch.delenv("TEST_NATIVE_PROTOCOL_KEY", raising=False)

    provider = OpenAICompatibleProvider(
        base_url="http://localhost:8000/v1",
        model="test-model",
        api_key_env="TEST_NATIVE_PROTOCOL_KEY",
        urlopen=lambda *_args, **_kwargs: pytest.fail(
            "HTTP request must not run"
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="API key environment variable is not set",
    ):
        provider.generate(LLMRequest(messages=[]))


def test_native_protocol_contract_does_not_store_api_key(
    monkeypatch,
) -> None:
    monkeypatch.setenv("TEST_NATIVE_PROTOCOL_KEY", "secret-value")

    provider = OpenAICompatibleProvider(
        base_url="http://localhost:8000/v1",
        model="test-model",
        api_key_env="TEST_NATIVE_PROTOCOL_KEY",
    )

    assert "secret-value" not in repr(provider.__dict__)
    assert provider.__dict__["_api_key_env"] == "TEST_NATIVE_PROTOCOL_KEY"
