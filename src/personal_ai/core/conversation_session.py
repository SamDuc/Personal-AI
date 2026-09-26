from personal_ai.core.llm import ChatMessage


class ConversationSession:
    def __init__(self, session_id: str | None = None) -> None:
        if session_id is None:
            session_id = "session"

        if not isinstance(session_id, str) or not session_id:
            raise ValueError("session_id must be a non-empty string")

        self.session_id = session_id
        self.messages: list[ChatMessage] = []

    def add_message(self, message: ChatMessage) -> None:
        if not isinstance(message, ChatMessage):
            raise ValueError("message must be a ChatMessage")

        self.messages.append(message)

    def get_messages(self) -> list[ChatMessage]:
        return list(self.messages)
