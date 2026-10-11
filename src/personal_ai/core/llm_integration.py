from personal_ai.core.conversation_session import ConversationSession
from personal_ai.core.llm import (
    ChatMessage,
    LLMRequest,
    LLMResponse,
    LLMToolDefinition,
)
from personal_ai.core.llm_runtime import LLMRuntime


class LLMIntegration:
    def __init__(self, runtime: LLMRuntime) -> None:
        self.runtime = runtime

    def generate(
        self,
        session: ConversationSession,
        tools: tuple[LLMToolDefinition, ...] = (),
    ) -> LLMResponse:
        request = LLMRequest(
            messages=session.get_messages(),
            tools=tools,
        )

        response = self.runtime.generate(request)

        assistant_message = ChatMessage(
            role="assistant",
            content=response.text,
            tool_calls=response.tool_calls,
        )

        session.add_message(assistant_message)

        return response
