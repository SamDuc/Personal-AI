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

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            result = self._body
            self._body = b""
            return result

        result = self._body[:size]
        self._body = self._body[size:]
        return result


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

def test_generate_preserves_http_401_status() -> None:
    from urllib.error import HTTPError

    provider = OpenAICompatibleProvider(
        base_url="http://localhost:8000/v1",
        model="test-model",
        urlopen=lambda *_args, **_kwargs: (_ for _ in ()).throw(
            HTTPError(
                url="http://localhost:8000/v1/chat/completions",
                code=401,
                msg="Unauthorized",
                hdrs=None,
                fp=None,
            )
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="OpenAI-compatible provider request failed with HTTP 401",
    ):
        provider.generate(
            LLMRequest(
                messages=[
                    ChatMessage(role="user", content="test"),
                ]
            )
        )


def test_generate_preserves_http_402_status() -> None:
    from urllib.error import HTTPError

    provider = OpenAICompatibleProvider(
        base_url="http://localhost:8000/v1",
        model="test-model",
        urlopen=lambda *_args, **_kwargs: (_ for _ in ()).throw(
            HTTPError(
                url="http://localhost:8000/v1/chat/completions",
                code=402,
                msg="Payment Required",
                hdrs=None,
                fp=None,
            )
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="OpenAI-compatible provider request failed with HTTP 402",
    ):
        provider.generate(
            LLMRequest(
                messages=[
                    ChatMessage(role="user", content="test"),
                ]
            )
        )


def test_generate_preserves_http_429_status() -> None:
    from urllib.error import HTTPError

    provider = OpenAICompatibleProvider(
        base_url="http://localhost:8000/v1",
        model="test-model",
        urlopen=lambda *_args, **_kwargs: (_ for _ in ()).throw(
            HTTPError(
                url="http://localhost:8000/v1/chat/completions",
                code=429,
                msg="Too Many Requests",
                hdrs=None,
                fp=None,
            )
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="OpenAI-compatible provider request failed with HTTP 429",
    ):
        provider.generate(
            LLMRequest(
                messages=[
                    ChatMessage(role="user", content="test"),
                ]
            )
        )

def test_generate_preserves_response_text_exactly() -> None:
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


def test_generate_rejects_non_text_response_content() -> None:
    def fake_urlopen(req, timeout):
        return FakeHTTPResponse(
            b'{"choices":[{"message":{"content":{"text":"hello"}}}]}'
        )

    provider = OpenAICompatibleProvider(
        base_url="http://localhost:8000/v1",
        model="test-model",
        urlopen=fake_urlopen,
    )

    with pytest.raises(
        RuntimeError,
        match="response content must be text",
    ):
        provider.generate(LLMRequest(messages=[]))


def test_generate_parses_tool_calls() -> None:
    def fake_urlopen(req, timeout):
        body = {
            "choices": [
                {
                    "message": {
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_1",
                                "type": "function",
                                "function": {
                                    "name": "local_file_read",
                                    "arguments": json.dumps({"path": "notes.txt"}),
                                },
                            }
                        ],
                    }
                }
            ]
        }
        return FakeHTTPResponse(json.dumps(body).encode("utf-8"))

    provider = OpenAICompatibleProvider(
        base_url="http://localhost:8000/v1",
        model="test-model",
        urlopen=fake_urlopen,
    )

    response = provider.generate(LLMRequest(messages=[]))

    assert response.text == ""
    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].id == "call_1"
    assert response.tool_calls[0].name == "local_file_read"
    assert json.loads(response.tool_calls[0].arguments) == {"path": "notes.txt"}


@pytest.mark.parametrize(
    "tool_call",
    [
        {},
        {"id": "call_1", "function": {"arguments": "{}"}},
        {"id": "call_1", "function": {"name": "local_file_read"}},
        {"id": "call_1", "function": {"name": "local_file_read", "arguments": {}}},
    ],
)
def test_generate_rejects_malformed_tool_calls(tool_call) -> None:
    body = json.dumps(
        {
            "choices": [
                {
                    "message": {
                        "content": None,
                        "tool_calls": [tool_call],
                    }
                }
            ]
        }
    ).encode("utf-8")

    provider = OpenAICompatibleProvider(
        base_url="http://localhost:8000/v1",
        model="test-model",
        urlopen=lambda req, timeout: FakeHTTPResponse(body),
    )

    with pytest.raises(RuntimeError, match="malformed tool call"):
        provider.generate(LLMRequest(messages=[]))

def test_generate_serializes_assistant_tool_calls_and_tool_result() -> None:
    from personal_ai.core.llm import LLMToolCall

    captured = {}

    def fake_urlopen(req, timeout):
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return FakeHTTPResponse(
            b'{"choices":[{"message":{"content":"Done"}}]}'
        )

    provider = OpenAICompatibleProvider(
        base_url="http://localhost:8000/v1",
        model="test-model",
        urlopen=fake_urlopen,
    )

    call = LLMToolCall(
        id="call-123",
        name="local_file_read",
        arguments='{"path":"notes.txt"}',
    )

    provider.generate(
        LLMRequest(
            messages=[
                ChatMessage(role="user", content="Read notes.txt"),
                ChatMessage(
                    role="assistant",
                    content="",
                    tool_calls=(call,),
                ),
                ChatMessage(
                    role="tool",
                    content='{"status":"success","result":"hello","error":null}',
                    tool_call_id="call-123",
                ),
            ]
        )
    )

    messages = captured["body"]["messages"]

    assert messages[1] == {
        "role": "assistant",
        "content": "",
        "tool_calls": [
            {
                "id": "call-123",
                "type": "function",
                "function": {
                    "name": "local_file_read",
                    "arguments": '{"path":"notes.txt"}',
                },
            }
        ],
    }
    assert messages[2] == {
        "role": "tool",
        "content": '{"status":"success","result":"hello","error":null}',
        "tool_call_id": "call-123",
    }


def test_generate_rejects_oversized_response(monkeypatch) -> None:
    monkeypatch.delenv("TEST_LLM_API_KEY", raising=False)

    provider = OpenAICompatibleProvider(
        base_url="http://localhost:11434/v1",
        model="test-model",
        timeout=1,
        urlopen=lambda req, timeout: FakeHTTPResponse(
            b"x" * (10 * 1024 * 1024 + 1)
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="response exceeded the 10 MiB size limit",
    ):
        provider.generate(LLMRequest(messages=[ChatMessage(role="user", content="hi")]))