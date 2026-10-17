import json

import pytest

from personal_ai.core.agent import Agent
from personal_ai.core.audit import InMemoryAuditSink, make_audit_event
from personal_ai.core.conversation_session import ConversationSession
from personal_ai.core.llm import LLMResponse, LLMToolCall
from personal_ai.core.llm_integration import LLMIntegration
from personal_ai.core.llm_runtime import LLMRuntime
from personal_ai.retrieval.local import RetrievalRequest


class FakeRuntime(LLMRuntime):
    def __init__(self, response=None, error=None):
        self.response = response or LLMResponse(text="ok")
        self.error = error

    def generate(self, request):
        if self.error is not None:
            raise self.error
        return self.response


class FakeRetrieval:
    def __init__(self, error=None):
        self.error = error

    def retrieve(self, request: RetrievalRequest):
        if self.error is not None:
            raise self.error
        return []


def make_agent(*, runtime=None, audit_sink=None, **kwargs):
    integration = LLMIntegration(runtime or FakeRuntime())
    return Agent(
        integration,
        audit_sink=audit_sink,
        **kwargs,
    )


def test_generation_success_is_audited_without_prompt_content():
    sink = InMemoryAuditSink()
    agent = make_agent(
        runtime=FakeRuntime(LLMResponse(text="private answer")),
        audit_sink=sink,
    )

    agent.run("secret user prompt", ConversationSession())

    events = sink.get_events()
    assert len(events) == 1
    assert (events[0].event_type, events[0].outcome) == (
        "generation",
        "success",
    )
    assert events[0].operation == "llm_generate"
    assert "secret user prompt" not in repr(events)
    assert "private answer" not in repr(events)


def test_generation_failure_is_audited_and_original_error_preserved():
    sink = InMemoryAuditSink()
    error = RuntimeError("private provider error")
    agent = make_agent(
        runtime=FakeRuntime(error=error),
        audit_sink=sink,
    )

    with pytest.raises(RuntimeError) as caught:
        agent.run("private prompt", ConversationSession())

    assert caught.value is error
    events = sink.get_events()
    assert len(events) == 1
    assert events[0].event_type == "generation"
    assert events[0].outcome == "failure"
    assert "private prompt" not in repr(events)
    assert "private provider error" not in repr(events)


def test_retrieval_success_is_audited_without_query():
    sink = InMemoryAuditSink()
    agent = make_agent(
        audit_sink=sink,
        retrieval=FakeRetrieval(),
    )

    agent.run("private retrieval query", ConversationSession())

    events = sink.get_events()
    assert [(e.event_type, e.outcome) for e in events] == [
        ("retrieval", "success"),
        ("generation", "success"),
    ]
    assert "private retrieval query" not in repr(events)


def test_retrieval_failure_is_audited_and_propagated():
    sink = InMemoryAuditSink()
    error = RuntimeError("private retrieval error")
    agent = make_agent(
        audit_sink=sink,
        retrieval=FakeRetrieval(error=error),
    )

    with pytest.raises(RuntimeError) as caught:
        agent.run("private query", ConversationSession())

    assert caught.value is error
    events = sink.get_events()
    assert len(events) == 1
    assert (events[0].event_type, events[0].outcome) == (
        "retrieval",
        "failure",
    )
    assert "private query" not in repr(events)
    assert "private retrieval error" not in repr(events)


def test_denied_tool_call_is_audited_without_arguments_or_result():
    sink = InMemoryAuditSink()
    agent = make_agent(audit_sink=sink)

    call = LLMToolCall(
        id="call-1",
        name="unregistered_private_tool",
        arguments=json.dumps({"secret": "private-argument"}),
    )
    message = agent._handle_model_tool_call(call)
    payload = json.loads(message.content)

    assert payload["status"] == "unknown_tool"
    events = sink.get_events()
    assert len(events) == 1
    assert (events[0].event_type, events[0].outcome) == (
        "action",
        "failure",
    )
    assert events[0].operation == "unregistered_private_tool"
    assert "private-argument" not in repr(events)
    assert "private-argument" not in repr(payload)


def test_tool_execution_exception_emits_one_failure_event():
    sink = InMemoryAuditSink()
    agent = make_agent(audit_sink=sink)

    class RaisingAgent(Agent):
        def execute_registered_tool(self, **kwargs):
            raise RuntimeError("private tool exception")

    agent = RaisingAgent(
        LLMIntegration(FakeRuntime()),
        audit_sink=sink,
    )

    # A registered tool and valid permission evaluator are required to reach
    # execute_registered_tool. This test verifies the direct exception path
    # only if the tool-call reaches that point.
    from personal_ai.permissions.evaluator import PermissionEvaluator
    from personal_ai.permissions.policy import PermissionPolicy
    from personal_ai.tools.model import ToolDefinition
    from personal_ai.tools.registry import ToolRegistry
    from personal_ai.tools.tool import Tool

    class DummyTool(Tool):
        @property
        def definition(self):
            return ToolDefinition(
                name="dummy",
                description="test",
                resource_category="local_filesystem",
                operation="read",
                parameters={
                    "type": "object",
                    "properties": {"value": {"type": "string"}},
                    "required": ["value"],
                    "additionalProperties": False,
                },
            )

        def execute(self, input_data, permission_evaluator):
            raise AssertionError("must not execute directly")

    registry = ToolRegistry()
    registry.register(DummyTool())
    agent.tool_registry = registry
    agent.permission_evaluator = PermissionEvaluator(
        PermissionPolicy(
            {
                "defaults": {"local_filesystem": {"read": True}},
                "confirmation_required": [],
            }
        )
    )

    with pytest.raises(RuntimeError, match="private tool exception"):
        agent._handle_model_tool_call(
            LLMToolCall(
                id="call-2",
                name="dummy",
                arguments='{"value":"private-value"}',
            )
        )

    events = sink.get_events()
    assert len(events) == 2
    assert [(event.event_type, event.outcome) for event in events] == [
        ("action", "intent"),
        ("action", "failure"),
    ]
    assert all(event.operation == "dummy" for event in events)
    assert events[0].correlation_id
    assert events[0].correlation_id == events[1].correlation_id
    assert "private-value" not in repr(events)
    assert "private tool exception" not in repr(events)


def test_registered_tool_denied_by_permission_is_audited():
    from personal_ai.permissions.evaluator import PermissionEvaluator
    from personal_ai.permissions.policy import PermissionPolicy
    from personal_ai.tools.model import ToolDefinition
    from personal_ai.tools.registry import ToolRegistry
    from personal_ai.tools.tool import Tool

    sink = InMemoryAuditSink()
    agent = make_agent(audit_sink=sink)

    class DummyTool(Tool):
        @property
        def definition(self):
            return ToolDefinition(
                name="dummy_denied",
                description="test",
                resource_category="local_filesystem",
                operation="read",
                parameters={
                    "type": "object",
                    "properties": {"value": {"type": "string"}},
                    "required": ["value"],
                    "additionalProperties": False,
                },
            )

        def execute(self, input_data, permission_evaluator):
            raise AssertionError("Denied tool must not execute")

    registry = ToolRegistry()
    registry.register(DummyTool())
    agent.tool_registry = registry
    agent.permission_evaluator = PermissionEvaluator(
        PermissionPolicy(
            {
                "defaults": {"local_filesystem": {"read": False}},
                "confirmation_required": [],
            }
        )
    )

    message = agent._handle_model_tool_call(
        LLMToolCall(
            id="call-denied",
            name="dummy_denied",
            arguments='{"value":"private-value"}',
        )
    )

    payload = json.loads(message.content)
    events = sink.get_events()

    assert payload["status"] == "denied"
    assert len(events) == 2
    assert [(event.event_type, event.outcome) for event in events] == [
        ("action", "intent"),
        ("action", "failure"),
    ]
    assert all(event.operation == "dummy_denied" for event in events)
    assert events[0].correlation_id
    assert events[0].correlation_id == events[1].correlation_id
    assert "private-value" not in repr(events)


def test_confirmation_required_is_audited_without_executing_tool():
    from personal_ai.permissions.evaluator import PermissionEvaluator
    from personal_ai.permissions.policy import PermissionPolicy
    from personal_ai.tools.model import ToolDefinition, ToolResult
    from personal_ai.tools.registry import ToolRegistry
    from personal_ai.tools.tool import Tool

    sink = InMemoryAuditSink()
    agent = make_agent(audit_sink=sink)

    class ConfirmationTool(Tool):
        def __init__(self):
            self.execution_count = 0

        @property
        def definition(self):
            return ToolDefinition(
                name="confirmation_probe",
                description="Test confirmation-required boundary",
                resource_category="local_filesystem",
                operation="read",
                parameters={
                    "type": "object",
                    "properties": {
                        "value": {"type": "string"},
                    },
                    "required": ["value"],
                    "additionalProperties": False,
                },
            )

        def execute(self, input_data, permission_evaluator):
            self.execution_count += 1
            return ToolResult(status="success", result=input_data)

    tool = ConfirmationTool()
    registry = ToolRegistry()
    registry.register(tool)

    agent.tool_registry = registry
    agent.permission_evaluator = PermissionEvaluator(
        PermissionPolicy(
            {
                "defaults": {
                    "local_filesystem": {"read": True},
                },
                "confirmation_required": ["read"],
            }
        )
    )

    message = agent._handle_model_tool_call(
        LLMToolCall(
            id="call-confirmation-required",
            name="confirmation_probe",
            arguments='{"value":"private-confirmation-value"}',
        )
    )

    payload = json.loads(message.content)
    events = sink.get_events()

    assert payload["status"] == "confirmation_required"
    assert tool.execution_count == 0

    assert len(events) == 2
    assert [(event.event_type, event.outcome) for event in events] == [
        ("action", "intent"),
        ("action", "failure"),
    ]
    assert all(event.operation == "confirmation_probe" for event in events)
    assert events[0].correlation_id
    assert events[0].correlation_id == events[1].correlation_id
    assert "private-confirmation-value" not in repr(events)


def test_audit_sink_failure_is_not_silently_ignored():
    class FailingSink:
        def emit(self, event):
            raise OSError("audit sink unavailable")

    agent = make_agent(audit_sink=FailingSink())

    with pytest.raises(OSError, match="audit sink unavailable"):
        agent.run("private prompt", ConversationSession())


@pytest.mark.parametrize("correlation_id", ["", "   ", "\t"])
def test_make_audit_event_rejects_blank_correlation_id(correlation_id):
    with pytest.raises(ValueError, match="correlation_id"):
        make_audit_event(
            event_type="action",
            outcome="intent",
            operation="test",
            correlation_id=correlation_id,
        )

@pytest.mark.parametrize(
    ("event_type", "outcome"),
    [
        ([], "success"),
        ("generation", []),
    ],
)


def test_make_audit_event_rejects_unhashable_values(event_type, outcome):
    with pytest.raises(ValueError):
        make_audit_event(
            event_type=event_type,
            outcome=outcome,
            operation="test",
        )


def test_audit_sink_custom_exception_does_not_mask_generation_error():
    class CustomAuditError(Exception):
        pass

    class FailingSink:
        def emit(self, event):
            raise CustomAuditError("sensitive audit sink detail")

    original_error = RuntimeError("original generation failure")
    agent = make_agent(
        runtime=FakeRuntime(error=original_error),
        audit_sink=FailingSink(),
    )

    with pytest.raises(RuntimeError) as caught:
        agent.run("private prompt", ConversationSession())

    assert caught.value is original_error
    notes = getattr(caught.value, "__notes__", [])
    assert any("CustomAuditError" in note for note in notes)
    assert all("sensitive audit sink detail" not in note for note in notes)


def test_audit_sink_failure_does_not_mask_retrieval_error():
    class FailingSink:
        def emit(self, event):
            raise OSError("sensitive audit sink detail")

    original_error = RuntimeError("original retrieval failure")
    agent = make_agent(
        audit_sink=FailingSink(),
        retrieval=FakeRetrieval(error=original_error),
    )

    with pytest.raises(RuntimeError) as caught:
        agent.run("private query", ConversationSession())

    assert caught.value is original_error
    notes = getattr(caught.value, "__notes__", [])
    assert any("OSError" in note for note in notes)
    assert all("sensitive audit sink detail" not in note for note in notes)


def test_terminal_audit_failure_preserves_original_tool_error():
    from personal_ai.permissions.evaluator import PermissionEvaluator
    from personal_ai.permissions.policy import PermissionPolicy
    from personal_ai.tools.model import ToolDefinition
    from personal_ai.tools.registry import ToolRegistry
    from personal_ai.tools.tool import Tool

    original_error = RuntimeError("original tool failure")

    class FailOnTerminalSink:
        def __init__(self):
            self.events = []

        def emit(self, event):
            if event.outcome != "intent":
                raise OSError("sensitive terminal audit failure")
            self.events.append(event)

    class DummyTool(Tool):
        @property
        def definition(self):
            return ToolDefinition(
                name="dummy_terminal_audit",
                description="test",
                resource_category="local_filesystem",
                operation="read",
                parameters={
                    "type": "object",
                    "properties": {"value": {"type": "string"}},
                    "required": ["value"],
                    "additionalProperties": False,
                },
            )

        def execute(self, input_data, permission_evaluator):
            raise AssertionError("Tool execution must use the agent path")

    class RaisingAgent(Agent):
        def execute_registered_tool(self, **kwargs):
            raise original_error

    sink = FailOnTerminalSink()
    agent = RaisingAgent(
        LLMIntegration(FakeRuntime()),
        audit_sink=sink,
    )
    registry = ToolRegistry()
    registry.register(DummyTool())
    agent.tool_registry = registry
    agent.permission_evaluator = PermissionEvaluator(
        PermissionPolicy(
            {
                "defaults": {"local_filesystem": {"read": True}},
                "confirmation_required": [],
            }
        )
    )

    with pytest.raises(RuntimeError) as caught:
        agent._handle_model_tool_call(
            LLMToolCall(
                id="call-terminal-audit-failure",
                name="dummy_terminal_audit",
                arguments='{"value":"private-value"}',
            )
        )

    assert caught.value is original_error
    assert len(sink.events) == 1
    assert sink.events[0].outcome == "intent"
    assert sink.events[0].correlation_id
    notes = getattr(caught.value, "__notes__", [])
    assert any("OSError" in note for note in notes)
    assert all("sensitive terminal audit failure" not in note for note in notes)
    assert "private-value" not in repr(sink.events)


def test_audit_intent_sink_failure_prevents_tool_execution():
    from personal_ai.permissions.evaluator import PermissionEvaluator
    from personal_ai.permissions.policy import PermissionPolicy
    from personal_ai.tools.model import ToolDefinition
    from personal_ai.tools.registry import ToolRegistry
    from personal_ai.tools.tool import Tool

    class FailingSink:
        def emit(self, event):
            raise OSError("audit storage unavailable")

    class DummyTool(Tool):
        @property
        def definition(self):
            return ToolDefinition(
                name="dummy_audit_failure",
                description="test",
                resource_category="local_filesystem",
                operation="read",
                parameters={
                    "type": "object",
                    "properties": {"value": {"type": "string"}},
                    "required": ["value"],
                    "additionalProperties": False,
                },
            )

        def execute(self, input_data, permission_evaluator):
            raise AssertionError("Tool execution must use the agent path")

    execution_attempts = 0

    class RaisingAgent(Agent):
        def execute_registered_tool(self, **kwargs):
            nonlocal execution_attempts
            execution_attempts += 1
            raise RuntimeError("tool must not be reached")

    agent = RaisingAgent(
        LLMIntegration(FakeRuntime()),
        audit_sink=FailingSink(),
    )
    registry = ToolRegistry()
    registry.register(DummyTool())
    agent.tool_registry = registry
    agent.permission_evaluator = PermissionEvaluator(
        PermissionPolicy(
            {
                "defaults": {"local_filesystem": {"read": True}},
                "confirmation_required": [],
            }
        )
    )

    with pytest.raises(OSError, match="audit storage unavailable"):
        agent._handle_model_tool_call(
            LLMToolCall(
                id="call-audit-failure",
                name="dummy_audit_failure",
                arguments='{"value":"private-value"}',
            )
        )

    assert execution_attempts == 0


@pytest.mark.parametrize("raise_error", [False, True])
def test_agent_holds_action_lock_through_tool_and_terminal_audit(raise_error):
    from contextlib import contextmanager

    from personal_ai.permissions.evaluator import PermissionEvaluator
    from personal_ai.permissions.policy import PermissionPolicy
    from personal_ai.tools.model import ToolDefinition, ToolResult
    from personal_ai.tools.registry import ToolRegistry
    from personal_ai.tools.tool import Tool

    class TrackingSink:
        def __init__(self):
            self.lock_held = False
            self.events = []

        @contextmanager
        def action_lock(self, correlation_id):
            assert correlation_id
            assert not self.lock_held
            self.lock_held = True
            try:
                yield
            finally:
                self.lock_held = False

        def emit(self, event):
            assert self.lock_held, (
                "Audit event was emitted outside the action ownership lock"
            )
            self.events.append(event)

    class DummyTool(Tool):
        @property
        def definition(self):
            return ToolDefinition(
                name="ownership_lock_probe",
                description="Test ownership lock lifetime",
                resource_category="local_filesystem",
                operation="read",
                parameters={
                    "type": "object",
                    "properties": {"value": {"type": "string"}},
                    "required": ["value"],
                    "additionalProperties": False,
                },
            )

        def execute(self, input_data, permission_evaluator):
            raise AssertionError("Execution must use the Agent path")

    sink = TrackingSink()
    original_error = RuntimeError("private tool failure")

    class TrackingAgent(Agent):
        def execute_registered_tool(self, **kwargs):
            assert sink.lock_held, (
                "Ownership lock was not held during tool execution"
            )
            if raise_error:
                raise original_error
            return ToolResult(status="success", result={"ok": True})

    agent = TrackingAgent(
        LLMIntegration(FakeRuntime()),
        audit_sink=sink,
    )

    registry = ToolRegistry()
    registry.register(DummyTool())
    agent.tool_registry = registry
    agent.permission_evaluator = PermissionEvaluator(
        PermissionPolicy(
            {
                "defaults": {"local_filesystem": {"read": True}},
                "confirmation_required": [],
            }
        )
    )

    call = LLMToolCall(
        id="call-ownership-lock",
        name="ownership_lock_probe",
        arguments='{"value":"private-value"}',
    )

    if raise_error:
        with pytest.raises(RuntimeError) as caught:
            agent._handle_model_tool_call(call)
        assert caught.value is original_error
        expected_outcomes = ["intent", "failure"]
    else:
        agent._handle_model_tool_call(call)
        expected_outcomes = ["intent", "success"]

    assert sink.lock_held is False, "Ownership lock was not released"
    assert [event.outcome for event in sink.events] == expected_outcomes
    assert all(event.event_type == "action" for event in sink.events)
    assert sink.events[0].correlation_id
    assert all(
        event.correlation_id == sink.events[0].correlation_id
        for event in sink.events
    )
    assert "private-value" not in repr(sink.events)
    assert "private tool failure" not in repr(sink.events)
