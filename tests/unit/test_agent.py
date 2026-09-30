import pytest

from personal_ai.core.agent import Agent
from personal_ai.core.conversation_session import ConversationSession
from personal_ai.core.executor import Executor
from personal_ai.core.llm import ChatMessage, LLMResponse
from personal_ai.core.llm_integration import LLMIntegration
from personal_ai.core.llm_runtime import LLMRuntime


class FakeRuntime(LLMRuntime):
    def __init__(self, response: LLMResponse) -> None:
        self.response = response
        self.call_count = 0

    def generate(self, request):
        self.call_count += 1
        return self.response


class FailingRuntime(LLMRuntime):
    def __init__(self) -> None:
        pass

    def generate(self, request):
        raise RuntimeError("generation failed")


def test_agent_preserves_user_request() -> None:
    session = ConversationSession()

    runtime = FakeRuntime(
        LLMResponse(text="Hello from assistant"),
    )
    integration = LLMIntegration(runtime)
    agent = Agent(integration)

    agent.run("Hello, this is my request.", session)

    assert session.messages[0] == ChatMessage(
        role="user",
        content="Hello, this is my request.",
    )


def test_agent_uses_existing_conversation_session() -> None:
    session = ConversationSession()

    existing_message = ChatMessage(
        role="user",
        content="Previous message",
    )
    session.add_message(existing_message)

    runtime = FakeRuntime(
        LLMResponse(text="Response"),
    )
    integration = LLMIntegration(runtime)
    agent = Agent(integration)

    agent.run("New request", session)

    assert session.messages[0] == existing_message
    assert session.messages[1] == ChatMessage(
        role="user",
        content="New request",
    )
    assert session.messages[2] == ChatMessage(
        role="assistant",
        content="Response",
    )


def test_agent_returns_generated_response_text() -> None:
    session = ConversationSession()

    runtime = FakeRuntime(
        LLMResponse(text="Generated response"),
    )
    integration = LLMIntegration(runtime)
    agent = Agent(integration)

    result = agent.run("Hello", session)

    assert result == "Generated response"


def test_agent_uses_llm_integration() -> None:
    session = ConversationSession()

    runtime = FakeRuntime(
        LLMResponse(text="Response"),
    )
    integration = LLMIntegration(runtime)
    agent = Agent(integration)

    agent.run("Hello", session)

    assert runtime.call_count == 1


def test_agent_rejects_non_string_user_request() -> None:
    session = ConversationSession()

    runtime = FakeRuntime(
        LLMResponse(text="Response"),
    )
    integration = LLMIntegration(runtime)
    agent = Agent(integration)

    with pytest.raises(ValueError):
        agent.run(123, session)


def test_agent_rejects_partial_planning_configuration() -> None:
    runtime = FakeRuntime(
        LLMResponse(text="Response"),
    )
    integration = LLMIntegration(runtime)

    with pytest.raises(
        ValueError,
        match="planner and executor must be provided together",
    ):
        Agent(
            integration,
            planner=object(),
        )


def test_agent_rejects_executor_without_planner() -> None:
    runtime = FakeRuntime(
        LLMResponse(text="Response"),
    )
    integration = LLMIntegration(runtime)

    with pytest.raises(
        ValueError,
        match="planner and executor must be provided together",
    ):
        Agent(
            integration,
            executor=Executor({}),
        )

def test_agent_does_not_claim_success_when_generation_fails() -> None:
    session = ConversationSession()

    runtime = FailingRuntime()
    integration = LLMIntegration(runtime)
    agent = Agent(integration)

    with pytest.raises(RuntimeError, match="generation failed"):
        agent.run("Hello", session)

    assert session.messages == [
        ChatMessage(
            role="user",
            content="Hello",
        ),
    ]
def test_agent_preserves_failure_identity() -> None:
    session = ConversationSession()

    class IdentityError(RuntimeError):
        pass

    failure = IdentityError("identity-preserved")

    class IdentityFailingRuntime(LLMRuntime):
        def __init__(self) -> None:
            pass

        def generate(self, request):
            raise failure

    integration = LLMIntegration(IdentityFailingRuntime())
    agent = Agent(integration)

    with pytest.raises(IdentityError) as exc_info:
        agent.run("Hello", session)

    assert exc_info.value is failure
    assert session.messages == [
        ChatMessage(role="user", content="Hello"),
    ]


def test_agent_preserves_existing_session_on_generation_failure() -> None:
    session = ConversationSession()

    existing_messages = [
        ChatMessage(role="user", content="Previous request"),
        ChatMessage(role="assistant", content="Previous response"),
    ]

    for message in existing_messages:
        session.add_message(message)

    class ExistingStateFailingRuntime(LLMRuntime):
        def __init__(self) -> None:
            pass

        def generate(self, request):
            raise RuntimeError("generation failed")

    integration = LLMIntegration(ExistingStateFailingRuntime())
    agent = Agent(integration)

    with pytest.raises(RuntimeError, match="generation failed"):
        agent.run("Current request", session)

    assert session.messages == [
        *existing_messages,
        ChatMessage(role="user", content="Current request"),
    ]


def test_agent_propagates_execution_failure() -> None:
    session = ConversationSession()

    class FailingExecutor:
        def with_capabilities(self, capabilities):
            return self

        def execute(self, plan):
            raise RuntimeError("execution failed")

    class StubPlanner:
        def plan(self, user_request):
            from personal_ai.core.planning import ExecutionPlan, PlanStep

            return ExecutionPlan(
                plan_id="plan-1",
                original_request=user_request,
                steps=(
                    PlanStep(
                        step_id="step-1",
                        capability="respond",
                        input_data=user_request,
                    ),
                ),
            )

    runtime = FakeRuntime(LLMResponse(text="unused"))
    integration = LLMIntegration(runtime)
    agent = Agent(
        integration,
        planner=StubPlanner(),
        executor=FailingExecutor(),
    )

    with pytest.raises(RuntimeError, match="execution failed"):
        agent.run("Execute this", session)

    assert session.messages == []
    assert runtime.call_count == 0
