import json
from typing import Self

from personal_ai.core.llm import ChatMessage, LLMRequest
from personal_ai.core.llm_config import LLMProviderConfig
from personal_ai.core.llm_factory import create_llm_provider


class FakeHTTPResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None

    def read(self) -> bytes:
        return self._payload


def test_factory_created_openai_provider_completes_mock_http_request(
    monkeypatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(http_request, timeout):
        captured["url"] = http_request.full_url
        captured["method"] = http_request.method
        captured["headers"] = dict(http_request.headers)
        captured["timeout"] = timeout
        captured["body"] = json.loads(http_request.data.decode("utf-8"))

        return FakeHTTPResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": "mock integration response",
                        }
                    }
                ]
            }
        )

    monkeypatch.setenv("TEST_LLM_API_KEY", "test-secret")
    monkeypatch.setattr(
        "personal_ai.core.openai_compatible.request.urlopen",
        fake_urlopen,
    )

    config = LLMProviderConfig(
        version=2,
        providers={
            "my_llm": {
                "enabled": True,
                "type": "cloud",
                "adapter": "openai_compatible",
                "base_url": "http://localhost:8000/v1",
                "model": "test-model",
                "api_key_env": "TEST_LLM_API_KEY",
            }
        },
    )

    provider = create_llm_provider(config, "my_llm")

    response = provider.generate(
        LLMRequest(
            messages=[
                ChatMessage(
                    role="user",
                    content="Xin chào",
                ),
            ]
        )
    )

    assert response.text == "mock integration response"
    assert captured["url"] == "http://localhost:8000/v1/chat/completions"
    assert captured["method"] == "POST"
    assert captured["timeout"] == 60.0
    assert captured["body"] == {
        "model": "test-model",
        "messages": [
            {
                "role": "user",
                "content": "Xin chào",
            }
        ],
    }

    headers = captured["headers"]
    assert isinstance(headers, dict)
    normalized_headers = {
        key.lower(): value
        for key, value in headers.items()
    }
    assert normalized_headers["content-type"] == "application/json"
    assert normalized_headers["authorization"] == "Bearer test-secret"


def test_factory_created_openai_provider_works_without_api_key_header(
    monkeypatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(http_request, timeout):
        captured["headers"] = dict(http_request.headers)
        return FakeHTTPResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": "local mock response",
                        }
                    }
                ]
            }
        )

    monkeypatch.delenv("TEST_LLM_API_KEY", raising=False)
    monkeypatch.setattr(
        "personal_ai.core.openai_compatible.request.urlopen",
        fake_urlopen,
    )

    config = LLMProviderConfig(
        version=2,
        providers={
            "local_llm": {
                "enabled": True,
                "type": "local",
                "adapter": "openai_compatible",
                "base_url": "http://localhost:8000/v1",
                "model": "local-model",
            }
        },
    )

    provider = create_llm_provider(config, "local_llm")

    response = provider.generate(
        LLMRequest(
            messages=[
                ChatMessage(
                    role="user",
                    content="hello",
                ),
            ]
        )
    )

    assert response.text == "local mock response"

    headers = captured["headers"]
    assert isinstance(headers, dict)
    assert "Authorization" not in headers
