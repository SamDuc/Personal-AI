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
