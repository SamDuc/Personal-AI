from personal_ai.core.conversation_session import ConversationSession
from personal_ai.core.llm import ChatMessage, LLMRequest, LLMResponse
from personal_ai.core.llm_integration import LLMIntegration
from personal_ai.core.llm_runtime import LLMRuntime


class FakeProviderA:
    def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(text="provider-a")


class FakeProviderB:
    def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(text="provider-b")


def test_runtime_accepts_different_provider_implementations() -> None:
    request = LLMRequest(
        messages=[
            ChatMessage(role="user", content="hello"),
        ]
    )

    response_a = LLMRuntime(FakeProviderA()).generate(request)
    response_b = LLMRuntime(FakeProviderB()).generate(request)

    assert response_a == LLMResponse(text="provider-a")
    assert response_b == LLMResponse(text="provider-b")


def test_integration_is_provider_independent() -> None:
    session_a = ConversationSession()
    session_b = ConversationSession()

    message_a = ChatMessage(role="user", content="hello")
    message_b = ChatMessage(role="user", content="hello")

    session_a.add_message(message_a)
    session_b.add_message(message_b)

    integration_a = LLMIntegration(LLMRuntime(FakeProviderA()))
    integration_b = LLMIntegration(LLMRuntime(FakeProviderB()))

    response_a = integration_a.generate(session_a)
    response_b = integration_b.generate(session_b)

    assert response_a == LLMResponse(text="provider-a")
    assert response_b == LLMResponse(text="provider-b")

    assert session_a.messages[-1] == ChatMessage(
        role="assistant",
        content="provider-a",
    )
    assert session_b.messages[-1] == ChatMessage(
        role="assistant",
        content="provider-b",
    )
