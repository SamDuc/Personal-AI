from personal_ai.core.agent import Agent
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


def test_agent_integrates_session_and_llm_boundary() -> None:
    session = ConversationSession(session_id="integration-session")
    runtime = IntegrationRuntime()
    integration = LLMIntegration(runtime)
    agent = Agent(integration)

    result = agent.run("Test integration request", session)

    assert result == "Integrated response"
    assert runtime.requests == [
        type(runtime.requests[0])(
            messages=[
                ChatMessage(
                    role="user",
                    content="Test integration request",
                ),
            ],
        )
    ]
    assert session.get_messages() == [
        ChatMessage(
            role="user",
            content="Test integration request",
        ),
        ChatMessage(
            role="assistant",
            content="Integrated response",
        ),
    ]
