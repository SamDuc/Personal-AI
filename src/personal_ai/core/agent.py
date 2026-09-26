from collections.abc import Callable

from personal_ai.core.conversation_session import ConversationSession
from personal_ai.core.llm import ChatMessage
from personal_ai.core.llm_integration import LLMIntegration


class Agent:
    def __init__(
        self,
        integration: LLMIntegration,
        retriever: Callable[[str], list[str]] | None = None,
    ) -> None:
        self.integration = integration
        self.retriever = retriever

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

        if self.retriever is not None:
            contexts = self.retriever(user_request)
            for context in contexts:
                session.add_message(
                    ChatMessage(
                        role="system",
                        content=f"Retrieved context:\n{context}",
                    )
                )

        response = self.integration.generate(session)

        return response.text
