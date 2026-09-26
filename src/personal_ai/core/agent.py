from personal_ai.core.conversation_session import ConversationSession
from personal_ai.core.llm import ChatMessage
from personal_ai.core.llm_integration import LLMIntegration


class Agent:
    def __init__(self, integration: LLMIntegration) -> None:
        self.integration = integration

    def run(
        self,
        user_request: str,
        session: ConversationSession,
    ) -> str:
        if not isinstance(user_request, str):
            raise ValueError("user_request must be a string")

        user_message = ChatMessage(
            role="user",
            content=user_request,
        )

        session.add_message(user_message)

        response = self.integration.generate(session)

        return response.text