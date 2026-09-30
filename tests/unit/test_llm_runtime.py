import pytest

from personal_ai.core.llm import (
    ChatMessage,
    LLMProvider,
    LLMRequest,
    LLMResponse,
)
from personal_ai.core.llm_factory import FakeLLMProvider
from personal_ai.core.llm_runtime import LLMRuntime


def test_runtime_accepts_llm_provider() -> None:
    provider = FakeLLMProvider()

    runtime = LLMRuntime(provider)

    assert isinstance(runtime.provider, LLMProvider)


def test_runtime_generates_response() -> None:
    provider = FakeLLMProvider()
    runtime = LLMRuntime(provider)

    request = LLMRequest(
        messages=[
            ChatMessage(role="user", content="Hello"),
        ],
    )

    response = runtime.generate(request)

    assert isinstance(response, LLMResponse)
    assert response.text


def test_runtime_returns_provider_response() -> None:
    class ControlledProvider(LLMProvider):
        def generate(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(text="controlled response")

    provider = ControlledProvider()
    runtime = LLMRuntime(provider)

    response = runtime.generate(
        LLMRequest(
            messages=[
                ChatMessage(role="user", content="Test"),
            ],
        )
    )

    assert response.text == "controlled response"


class FailingProvider(LLMProvider):
    def generate(self, request: LLMRequest) -> LLMResponse:
        raise RuntimeError("provider failure")


def test_runtime_propagates_provider_failure() -> None:
    runtime = LLMRuntime(FailingProvider())

    request = LLMRequest(
        messages=[
            ChatMessage(role="user", content="Hello"),
        ]
    )

    with pytest.raises(RuntimeError, match="provider failure"):
        runtime.generate(request)
