import pytest

from personal_ai.core.conversation_session import ConversationSession
from personal_ai.core.llm import (
    ChatMessage,
    LLMRequest,
    LLMResponse,
)
from personal_ai.core.llm_integration import LLMIntegration
from personal_ai.core.llm_runtime import LLMRuntime


class FakeRuntime(LLMRuntime):
    def __init__(self, response: LLMResponse) -> None:
        self.response = response
        self.received_request: LLMRequest | None = None

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.received_request = request
        return self.response


class FailingRuntime(LLMRuntime):
    def __init__(self) -> None:
        pass

    def generate(self, request: LLMRequest) -> LLMResponse:
        raise RuntimeError("generation failed")


def test_integration_constructs_request_from_session_messages() -> None:
    session = ConversationSession()

    first = ChatMessage(
        role="user",
        content="First",
    )
    second = ChatMessage(
        role="assistant",
        content="Second",
    )

    session.add_message(first)
    session.add_message(second)

    runtime = FakeRuntime(
        LLMResponse(text="Generated response"),
    )
    integration = LLMIntegration(runtime)

    integration.generate(session)

    assert runtime.received_request is not None
    assert runtime.received_request.messages == [first, second]


def test_integration_preserves_message_order_and_content() -> None:
    session = ConversationSession()

    first = ChatMessage(
        role="user",
        content="First message",
    )
    second = ChatMessage(
        role="user",
        content="Second message",
    )

    session.add_message(first)
    session.add_message(second)

    runtime = FakeRuntime(
        LLMResponse(text="Response"),
    )
    integration = LLMIntegration(runtime)

    integration.generate(session)

    request = runtime.received_request

    assert request is not None
    assert request.messages[0].role == "user"
    assert request.messages[0].content == "First message"
    assert request.messages[1].role == "user"
    assert request.messages[1].content == "Second message"


def test_integration_appends_assistant_response() -> None:
    session = ConversationSession()

    user_message = ChatMessage(
        role="user",
        content="Hello",
    )
    session.add_message(user_message)

    runtime = FakeRuntime(
        LLMResponse(text="Hello from assistant"),
    )
    integration = LLMIntegration(runtime)

    integration.generate(session)

    assert session.messages == [
        user_message,
        ChatMessage(
            role="assistant",
            content="Hello from assistant",
        ),
    ]


def test_integration_returns_llm_response() -> None:
    session = ConversationSession()

    runtime = FakeRuntime(
        LLMResponse(text="Generated response"),
    )
    integration = LLMIntegration(runtime)

    response = integration.generate(session)

    assert response == LLMResponse(text="Generated response")


def test_integration_does_not_append_on_generation_failure() -> None:
    session = ConversationSession()

    user_message = ChatMessage(
        role="user",
        content="Hello",
    )
    session.add_message(user_message)

    runtime = FailingRuntime()
    integration = LLMIntegration(runtime)

    with pytest.raises(RuntimeError, match="generation failed"):
        integration.generate(session)

    assert session.messages == [user_message]


def test_integration_does_not_modify_existing_messages() -> None:
    session = ConversationSession()

    message = ChatMessage(
        role="user",
        content="Original content",
    )
    session.add_message(message)

    runtime = FakeRuntime(
        LLMResponse(text="Response"),
    )
    integration = LLMIntegration(runtime)

    integration.generate(session)

    assert session.messages[0].role == "user"
    assert session.messages[0].content == "Original content"