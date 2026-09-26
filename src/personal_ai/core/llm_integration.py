from personal_ai.core.conversation_session import ConversationSession
from personal_ai.core.llm import (
    ChatMessage,
    LLMRequest,
    LLMResponse,
)
from personal_ai.core.llm_runtime import LLMRuntime


class LLMIntegration:
    def __init__(self, runtime: LLMRuntime) -> None:
        self.runtime = runtime

    def generate(self, session: ConversationSession) -> LLMResponse:
        request = LLMRequest(
            messages=session.get_messages(),
        )

        response = self.runtime.generate(request)

        assistant_message = ChatMessage(
            role="assistant",
            content=response.text,
        )

        session.add_message(assistant_message)

        return response