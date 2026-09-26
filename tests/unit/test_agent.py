import pytest

from personal_ai.core.agent import Agent
from personal_ai.core.conversation_session import ConversationSession
from personal_ai.core.llm import ChatMessage, LLMResponse
from personal_ai.core.llm_integration import LLMIntegration
from personal_ai.core.llm_runtime import LLMRuntime


class FakeRuntime(LLMRuntime):
    def __init__(self, response: LLMResponse) -> None:
        self.response = response
        self.call_count = 0

    def generate(self, request):
        self.call_count += 1
        return self.response


class FailingRuntime(LLMRuntime):
    def __init__(self) -> None:
        pass

    def generate(self, request):
        raise RuntimeError("generation failed")


def test_agent_preserves_user_request() -> None:
    session = ConversationSession()

    runtime = FakeRuntime(
        LLMResponse(text="Hello from assistant"),
    )
    integration = LLMIntegration(runtime)
    agent = Agent(integration)

    agent.run("Hello, this is my request.", session)

    assert session.messages[0] == ChatMessage(
        role="user",
        content="Hello, this is my request.",
    )


def test_agent_uses_existing_conversation_session() -> None:
    session = ConversationSession()

    existing_message = ChatMessage(
        role="user",
        content="Previous message",
    )
    session.add_message(existing_message)

    runtime = FakeRuntime(
        LLMResponse(text="Response"),
    )
    integration = LLMIntegration(runtime)
    agent = Agent(integration)

    agent.run("New request", session)

    assert session.messages[0] == existing_message
    assert session.messages[1] == ChatMessage(
        role="user",
        content="New request",
    )
    assert session.messages[2] == ChatMessage(
        role="assistant",
        content="Response",
    )


def test_agent_returns_generated_response_text() -> None:
    session = ConversationSession()

    runtime = FakeRuntime(
        LLMResponse(text="Generated response"),
    )
    integration = LLMIntegration(runtime)
    agent = Agent(integration)

    result = agent.run("Hello", session)

    assert result == "Generated response"


def test_agent_uses_llm_integration() -> None:
    session = ConversationSession()

    runtime = FakeRuntime(
        LLMResponse(text="Response"),
    )
    integration = LLMIntegration(runtime)
    agent = Agent(integration)

    agent.run("Hello", session)

    assert runtime.call_count == 1


def test_agent_rejects_non_string_user_request() -> None:
    session = ConversationSession()

    runtime = FakeRuntime(
        LLMResponse(text="Response"),
    )
    integration = LLMIntegration(runtime)
    agent = Agent(integration)

    with pytest.raises(ValueError):
        agent.run(123, session)


def test_agent_does_not_claim_success_when_generation_fails() -> None:
    session = ConversationSession()

    runtime = FailingRuntime()
    integration = LLMIntegration(runtime)
    agent = Agent(integration)

    with pytest.raises(RuntimeError, match="generation failed"):
        agent.run("Hello", session)

    assert session.messages == [
        ChatMessage(
            role="user",
            content="Hello",
        ),
    ]