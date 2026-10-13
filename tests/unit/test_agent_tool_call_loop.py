import json
from pathlib import Path

from personal_ai.core.agent import Agent
from personal_ai.core.conversation_session import ConversationSession
from personal_ai.core.llm import LLMRequest, LLMResponse, LLMToolCall
from personal_ai.core.llm_integration import LLMIntegration
from personal_ai.core.llm_runtime import LLMRuntime
from personal_ai.filesystem.scope import FilesystemAccessScope
from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.permissions.policy import PermissionPolicy
from personal_ai.tools.local_file_read import LocalFileReadTool
from personal_ai.tools.registry import ToolRegistry


class SequenceRuntime(LLMRuntime):
    def __init__(self, responses: list[LLMResponse]) -> None:
        self.responses = list(responses)
        self.requests: list[LLMRequest] = []

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        if not self.responses:
            raise AssertionError("Unexpected additional LLM request")
        return self.responses.pop(0)


def make_evaluator(read: bool) -> PermissionEvaluator:
    return PermissionEvaluator(
        PermissionPolicy(
            {
                "defaults": {
                    "local_filesystem": {"read": read},
                },
                "confirmation_required": [],
            }
        )
    )


def make_agent(
    runtime: SequenceRuntime,
    scope: FilesystemAccessScope,
    evaluator: PermissionEvaluator,
    *,
    max_tool_rounds: int = 5,
) -> Agent:
    registry = ToolRegistry()
    registry.register(LocalFileReadTool(filesystem_scope=scope))
    return Agent(
        integration=LLMIntegration(runtime),
        tool_registry=registry,
        permission_evaluator=evaluator,
        tool_calling_enabled=True,
        max_tool_rounds=max_tool_rounds,
    )


def test_agent_runs_tool_and_returns_follow_up_response(tmp_path: Path) -> None:
    target = tmp_path / "notes.txt"
    target.write_text("Hello from the file.", encoding="utf-8")

    runtime = SequenceRuntime(
        [
            LLMResponse(
                text="",
                tool_calls=(
                    LLMToolCall(
                        id="call-1",
                        name="local_file_read",
                        arguments=json.dumps({"path": str(target)}),
                    ),
                ),
            ),
            LLMResponse(text="The file says: Hello from the file."),
        ]
    )
    agent = make_agent(
        runtime,
        FilesystemAccessScope([tmp_path]),
        make_evaluator(read=True),
    )
    session = ConversationSession()

    answer = agent.run("Read notes.txt", session)

    assert answer == "The file says: Hello from the file."
    assert len(runtime.requests) == 2
    assert runtime.requests[0].tools[0].name == "local_file_read"

    follow_up_messages = runtime.requests[1].messages

    assistant_tool_messages = [
        message
        for message in follow_up_messages
        if message.role == "assistant" and message.tool_calls
    ]
    assert len(assistant_tool_messages) == 1

    assistant_tool_message = assistant_tool_messages[0]
    assert len(assistant_tool_message.tool_calls) == 1

    original_call = assistant_tool_message.tool_calls[0]
    assert original_call.id == "call-1"
    assert original_call.name == "local_file_read"
    assert json.loads(original_call.arguments) == {"path": str(target)}

    tool_messages = [
        message for message in follow_up_messages if message.role == "tool"
    ]
    assert len(tool_messages) == 1
    assert tool_messages[0].tool_call_id == original_call.id

    assistant_index = follow_up_messages.index(assistant_tool_message)
    tool_index = follow_up_messages.index(tool_messages[0])
    assert assistant_index < tool_index

    tool_payload = json.loads(tool_messages[0].content or "{}")
    assert tool_payload["status"] == "success"
    assert tool_payload["result"] == "Hello from the file."

    assert [message.role for message in session.get_messages()] == [
        "user",
        "assistant",
    ]


def test_agent_does_not_read_file_when_permission_is_denied(
    tmp_path: Path,
) -> None:
    target = tmp_path / "private.txt"
    target.write_text("Secret text.", encoding="utf-8")

    runtime = SequenceRuntime(
        [
            LLMResponse(
                text="",
                tool_calls=(
                    LLMToolCall(
                        id="call-denied",
                        name="local_file_read",
                        arguments=json.dumps({"path": str(target)}),
                    ),
                ),
            ),
            LLMResponse(text="I could not access that file."),
        ]
    )
    agent = make_agent(
        runtime,
        FilesystemAccessScope([tmp_path]),
        make_evaluator(read=False),
    )

    answer = agent.run("Read private.txt", ConversationSession())

    assert answer == "I could not access that file."
    tool_messages = [
        message
        for message in runtime.requests[1].messages
        if message.role == "tool"
    ]
    assert len(tool_messages) == 1
    payload = json.loads(tool_messages[0].content or "{}")
    assert payload["status"] == "denied"
    assert payload.get("result") is None


def test_agent_rejects_malformed_tool_arguments(tmp_path: Path) -> None:
    runtime = SequenceRuntime(
        [
            LLMResponse(
                text="",
                tool_calls=(
                    LLMToolCall(
                        id="call-invalid",
                        name="local_file_read",
                        arguments=json.dumps(
                            {"path": "notes.txt", "extra": "not allowed"}
                        ),
                    ),
                ),
            ),
            LLMResponse(text="The tool arguments were invalid."),
        ]
    )
    agent = make_agent(
        runtime,
        FilesystemAccessScope([tmp_path]),
        make_evaluator(read=True),
    )

    answer = agent.run("Read a file", ConversationSession())

    assert answer == "The tool arguments were invalid."
    tool_messages = [
        message
        for message in runtime.requests[1].messages
        if message.role == "tool"
    ]
    assert len(tool_messages) == 1
    payload = json.loads(tool_messages[0].content or "{}")
    assert payload["status"] == "invalid_input"


def test_agent_stops_after_tool_round_limit(tmp_path: Path) -> None:
    repeated_call = LLMResponse(
        text="",
        tool_calls=(
            LLMToolCall(
                id="call-loop",
                name="local_file_read",
                arguments=json.dumps({"path": str(tmp_path / "missing.txt")}),
            ),
        ),
    )
    runtime = SequenceRuntime([repeated_call, repeated_call])
    agent = make_agent(
        runtime,
        FilesystemAccessScope([tmp_path]),
        make_evaluator(read=True),
        max_tool_rounds=1,
    )

    answer = agent.run("Keep trying", ConversationSession())

    assert answer == "Tool call limit reached. Please try a simpler request."
    assert len(runtime.requests) == 2
