
from personal_ai.core.llm import (
    ChatMessage,
    LLMProvider,
    LLMRequest,
    LLMResponse,
)


def test_llm_request_contains_messages() -> None:
    request = LLMRequest(
        messages=[
            ChatMessage(role="user", content="Hello"),
        ]
    )

    assert request.messages[0].role == "user"
    assert request.messages[0].content == "Hello"


def test_llm_response_contains_text() -> None:
    response = LLMResponse(text="Hello back")

    assert response.text == "Hello back"


def test_llm_provider_is_replaceable_interface() -> None:
    class FakeProvider(LLMProvider):
        def generate(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(text="fake")

    provider = FakeProvider()

    result = provider.generate(
        LLMRequest(
            messages=[
                ChatMessage(role="user", content="test"),
            ]
        )
    )

    assert result.text == "fake"


def test_llm_request_does_not_require_specific_provider() -> None:
    request = LLMRequest(
        messages=[
            ChatMessage(role="system", content="You are a personal AI."),
            ChatMessage(role="user", content="Hello"),
        ]
    )

    assert len(request.messages) == 2

def test_chat_message_supports_structured_tool_calls() -> None:
    from personal_ai.core.llm import LLMToolCall

    call = LLMToolCall(
        id="call_1",
        name="local_file_read",
        arguments='{"path":"notes.txt"}',
    )
    message = ChatMessage(
        role="assistant",
        content=None,
        tool_calls=(call,),
    )

    assert message.content is None
    assert message.tool_calls == (call,)


def test_chat_message_supports_tool_result_reference() -> None:
    message = ChatMessage(
        role="tool",
        content="file contents",
        tool_call_id="call_1",
    )

    assert message.role == "tool"
    assert message.content == "file contents"
    assert message.tool_call_id == "call_1"


def test_llm_request_supports_tool_definitions() -> None:
    from personal_ai.core.llm import LLMToolDefinition

    tool = LLMToolDefinition(
        name="local_file_read",
        description="Read an authorized local text file.",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string"},
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    )
    request = LLMRequest(
        messages=[ChatMessage(role="user", content="Read notes.txt")],
        tools=(tool,),
    )

    assert request.tools == (tool,)
