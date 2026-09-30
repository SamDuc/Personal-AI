import pytest

from personal_ai.core.agent import Agent
from personal_ai.core.agent_router import AgentRoute, AgentRouter
from personal_ai.core.conversation_session import ConversationSession
from personal_ai.core.llm import ChatMessage, LLMResponse
from personal_ai.core.llm_integration import LLMIntegration
from personal_ai.core.llm_runtime import LLMRuntime


class IntegrationRuntime(LLMRuntime):
    def __init__(self) -> None:
        self.requests = []

    def generate(self, request):
        self.requests.append(request)
        return LLMResponse(text="Integrated response")


def test_router_dispatches_to_real_agent_and_llm_boundary() -> None:
    runtime = IntegrationRuntime()
    integration = LLMIntegration(runtime)
    agent = Agent(integration)

    router = AgentRouter(
        [AgentRoute(route_id="general", agent=agent)]
    )

    session = ConversationSession(session_id="router-integration-session")

    result = router.run(
        route_id="general",
        user_request="Test routed integration request",
        session=session,
    )

    assert result == "Integrated response"

    assert runtime.requests == [
        type(runtime.requests[0])(
            messages=[
                ChatMessage(
                    role="user",
                    content="Test routed integration request",
                ),
            ],
        )
    ]

    assert session.get_messages() == [
        ChatMessage(
            role="user",
            content="Test routed integration request",
        ),
        ChatMessage(
            role="assistant",
            content="Integrated response",
        ),
    ]

class FailingIntegrationRuntime(LLMRuntime):
    def __init__(self, failure: Exception) -> None:
        self.failure = failure

    def generate(self, request):
        raise self.failure


def test_router_propagates_llm_failure_without_fabricating_response() -> None:
    failure = RuntimeError("integration generation failed")
    runtime = FailingIntegrationRuntime(failure)
    integration = LLMIntegration(runtime)
    agent = Agent(integration)

    router = AgentRouter(
        [AgentRoute(route_id="general", agent=agent)]
    )

    session = ConversationSession(
        session_id="router-failure-integration-session"
    )
    session.add_message(
        ChatMessage(role="user", content="Previous request")
    )
    session.add_message(
        ChatMessage(role="assistant", content="Previous response")
    )

    with pytest.raises(RuntimeError) as exc_info:
        router.run(
            route_id="general",
            user_request="Current request",
            session=session,
        )

    assert exc_info.value is failure

    assert session.get_messages() == [
        ChatMessage(role="user", content="Previous request"),
        ChatMessage(role="assistant", content="Previous response"),
        ChatMessage(role="user", content="Current request"),
    ]
