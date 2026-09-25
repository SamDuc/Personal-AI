
from personal_ai.core.llm import (
    ChatMessage,
    LLMProvider,
    LLMRequest,
    LLMResponse,
)


def test_llm_request_contains_messages() -> None:
    request = LLMRequest(
        messages=[
            ChatMessage(role="user", content="Hello"),
        ]
    )

    assert request.messages[0].role == "user"
    assert request.messages[0].content == "Hello"


def test_llm_response_contains_text() -> None:
    response = LLMResponse(text="Hello back")

    assert response.text == "Hello back"


def test_llm_provider_is_replaceable_interface() -> None:
    class FakeProvider(LLMProvider):
        def generate(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(text="fake")

    provider = FakeProvider()

    result = provider.generate(
        LLMRequest(
            messages=[
                ChatMessage(role="user", content="test"),
            ]
        )
    )

    assert result.text == "fake"


def test_llm_request_does_not_require_specific_provider() -> None:
    request = LLMRequest(
        messages=[
            ChatMessage(role="system", content="You are a personal AI."),
            ChatMessage(role="user", content="Hello"),
        ]
    )

    assert len(request.messages) == 2
