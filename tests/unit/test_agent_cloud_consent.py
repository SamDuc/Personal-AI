from personal_ai.core.agent import Agent
from personal_ai.core.cloud_consent import (
    CloudConsentDeniedError,
    CloudConsentPendingError,
)
from personal_ai.core.conversation_session import ConversationSession
from personal_ai.core.llm import LLMRequest, LLMResponse
from personal_ai.core.llm_integration import LLMIntegration
from personal_ai.core.llm_runtime import LLMRuntime


class RecordingRuntime(LLMRuntime):
    def __init__(self) -> None:
        self.requests: list[LLMRequest] = []

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return LLMResponse(text="This response must not be generated.")


class ConsentFailureRuntime(LLMRuntime):
    def __init__(self, error: Exception) -> None:
        self.error = error
        self.calls = 0

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.calls += 1
        raise self.error


def make_agent(runtime: LLMRuntime) -> Agent:
    return Agent(integration=LLMIntegration(runtime))


def test_agent_returns_denied_message_without_retrying_cloud_request() -> None:
    runtime = ConsentFailureRuntime(CloudConsentDeniedError("cloud-test"))
    agent = make_agent(runtime)
    session = ConversationSession()

    answer = agent.run("Summarize my notes", session)

    assert answer == (
        "Cloud transfer to 'cloud-test' was denied. "
        "No data was sent by this request."
    )
    assert runtime.calls == 1
    assert [message.role for message in session.get_messages()] == ["user"]


def test_agent_returns_pending_message_without_retrying_cloud_request() -> None:
    runtime = ConsentFailureRuntime(CloudConsentPendingError("cloud-test"))
    agent = make_agent(runtime)
    session = ConversationSession()

    answer = agent.run("Summarize my notes", session)

    assert answer == (
        "Cloud transfer to 'cloud-test' is awaiting consent. "
        "No data was sent by this request."
    )
    assert runtime.calls == 1
    assert [message.role for message in session.get_messages()] == ["user"]


def test_agent_keeps_normal_response_behavior() -> None:
    runtime = RecordingRuntime()
    agent = make_agent(runtime)
    session = ConversationSession()

    answer = agent.run("Hello", session)

    assert answer == "This response must not be generated."
    assert len(runtime.requests) == 1
    assert [message.role for message in session.get_messages()] == [
        "user",
        "assistant",
    ]
