from __future__ import annotations

from personal_ai.core.conversation_session import ConversationSession
from personal_ai.core.llm import ChatMessage, LLMRequest, LLMResponse
from personal_ai.core.llm_integration import LLMIntegration
from personal_ai.core.llm_runtime import LLMRuntime


class FakeNativeProvider:
    def __init__(self) -> None:
        self.requests: list[LLMRequest] = []

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return LLMResponse(text="native-response")


def test_native_protocol_stays_behind_provider_boundary() -> None:
    provider = FakeNativeProvider()
    runtime = LLMRuntime(provider=provider)

    request = LLMRequest(
        messages=[ChatMessage(role="user", content="hello")]
    )

    response = runtime.generate(request)

    assert response.text == "native-response"
    assert len(provider.requests) == 1
    assert provider.requests[0].messages == request.messages


def test_native_provider_receives_structured_request_not_wire_payload() -> None:
    provider = FakeNativeProvider()
    runtime = LLMRuntime(provider=provider)

    request = LLMRequest(
        messages=[
            ChatMessage(role="system", content="system"),
            ChatMessage(role="user", content="question"),
        ]
    )

    runtime.generate(request)

    captured = provider.requests[0]

    assert isinstance(captured, LLMRequest)
    assert captured.messages[0].role == "system"
    assert captured.messages[1].role == "user"
    assert not isinstance(captured, dict)


def test_integration_appends_assistant_only_after_success() -> None:
    provider = FakeNativeProvider()
    runtime = LLMRuntime(provider=provider)
    integration = LLMIntegration(runtime=runtime)

    session = ConversationSession()
    session.add_message(
        ChatMessage(role="user", content="hello")
    )

    response = integration.generate(session)

    assert response.text == "native-response"

    messages = session.get_messages()

    assert messages[-1].role == "assistant"
    assert messages[-1].content == "native-response"
