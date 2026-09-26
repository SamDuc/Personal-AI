import pytest

from personal_ai.core.conversation_session import ConversationSession
from personal_ai.core.llm import ChatMessage


def test_session_has_stable_non_empty_id() -> None:
    session = ConversationSession()

    assert isinstance(session.session_id, str)
    assert session.session_id


def test_session_starts_with_empty_messages() -> None:
    session = ConversationSession()

    assert session.messages == []


def test_session_adds_message() -> None:
    session = ConversationSession()

    message = ChatMessage(
        role="user",
        content="Hello",
    )

    session.add_message(message)

    assert session.messages == [message]


def test_session_preserves_message_order() -> None:
    session = ConversationSession()

    first = ChatMessage(
        role="user",
        content="First",
    )
    second = ChatMessage(
        role="assistant",
        content="Second",
    )

    session.add_message(first)
    session.add_message(second)

    assert session.messages == [first, second]


def test_session_does_not_modify_message_content() -> None:
    session = ConversationSession()

    message = ChatMessage(
        role="user",
        content="Original content",
    )

    session.add_message(message)

    assert session.messages[0].role == "user"
    assert session.messages[0].content == "Original content"


def test_session_rejects_invalid_message() -> None:
    session = ConversationSession()

    with pytest.raises(ValueError):
        session.add_message("not a chat message")


def test_session_returns_ordered_messages() -> None:
    session = ConversationSession()

    first = ChatMessage(
        role="user",
        content="First",
    )
    second = ChatMessage(
        role="assistant",
        content="Second",
    )

    session.add_message(first)
    session.add_message(second)

    messages = session.get_messages()

    assert messages == [first, second]