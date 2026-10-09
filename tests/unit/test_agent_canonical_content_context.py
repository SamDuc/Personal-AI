import pytest

from personal_ai.core.agent import Agent
from personal_ai.core.conversation_session import ConversationSession
from personal_ai.core.llm import LLMResponse
from personal_ai.core.llm_integration import LLMIntegration
from personal_ai.core.llm_runtime import LLMRuntime
from personal_ai.core.models import DataItem
from personal_ai.retrieval.local import RetrievalRequest, RetrievalResult


class RecordingRuntime(LLMRuntime):
    def __init__(self):
        self.request = None

    def generate(self, request):
        self.request = request
        return LLMResponse(text="ok")


class RecordingRetrieval:
    def __init__(self, results):
        self.results = results
        self.requests = []

    def retrieve(self, request: RetrievalRequest) -> list[RetrievalResult]:
        self.requests.append(request)
        return list(self.results)


class RecordingContentAccess:
    def __init__(self, contents):
        self.contents = contents
        self.items = []

    def read(self, item: DataItem) -> str | None:
        self.items.append(item)
        return self.contents.get(item.id)


def make_item() -> DataItem:
    return DataItem(
        id="item-1",
        source="local_filesystem",
        source_id=r"C:\notes.txt",
        uri="file:///C:/notes.txt",
        item_type="file",
        mime_type="text/plain",
        extension=".txt",
        name="notes.txt",
        content_available=True,
        content_ref="index://content/abc",
        content_hash="abc",
        searchable=True,
        sync_status="indexed",
        access_policy=__import__(
            "personal_ai.core.models",
            fromlist=["AccessPolicy"],
        ).AccessPolicy(read=True, write=False),
    )


def test_agent_adds_retrieved_content_to_llm_context():
    runtime = RecordingRuntime()
    item = make_item()
    retrieval = RecordingRetrieval([RetrievalResult(item=item)])
    content_access = RecordingContentAccess(
        {"item-1": "The Raspberry Pi uses an ARM architecture."}
    )
    session = ConversationSession()

    agent = Agent(
        LLMIntegration(runtime),
        retrieval=retrieval,
        content_access=content_access,
    )

    result = agent.run("Explain Raspberry Pi architecture", session)

    assert result == "ok"
    assert content_access.items == [item]
    assert runtime.request is not None
    assert any(
        message.role == "user"
        and "The Raspberry Pi uses an ARM architecture." in message.content
        and "untrusted reference data" in message.content
        for message in runtime.request.messages
    )
    assert runtime.request.messages[-1].role == "user"
    assert runtime.request.messages[-1].content == (
        "Explain Raspberry Pi architecture"
    )


def test_agent_skips_unavailable_retrieved_content():
    runtime = RecordingRuntime()
    item = make_item()
    retrieval = RecordingRetrieval([RetrievalResult(item=item)])
    content_access = RecordingContentAccess({"item-1": None})

    agent = Agent(
        LLMIntegration(runtime),
        retrieval=retrieval,
        content_access=content_access,
    )

    assert agent.run("notes", ConversationSession()) == "ok"
    assert runtime.request is not None
    assert not any(
        message.role == "system" and "Retrieved context:" in message.content
        for message in runtime.request.messages
    )


def test_agent_propagates_content_access_failure():
    runtime = RecordingRuntime()
    item = make_item()
    retrieval = RecordingRetrieval([RetrievalResult(item=item)])

    class FailingContentAccess:
        def read(self, item: DataItem) -> str | None:
            raise RuntimeError("content access failed")

    agent = Agent(
        LLMIntegration(runtime),
        retrieval=retrieval,
        content_access=FailingContentAccess(),
    )

    with pytest.raises(RuntimeError, match="content access failed"):
        agent.run("notes", ConversationSession())

    assert runtime.request is None


def test_agent_does_not_read_content_when_retrieval_is_empty():
    runtime = RecordingRuntime()
    retrieval = RecordingRetrieval([])
    content_access = RecordingContentAccess({})

    agent = Agent(
        LLMIntegration(runtime),
        retrieval=retrieval,
        content_access=content_access,
    )

    assert agent.run("nothing found", ConversationSession()) == "ok"
    assert content_access.items == []
    assert runtime.request is not None
def test_agent_does_not_leave_partial_retrieved_context_on_failure():
    runtime = RecordingRuntime()
    first_item = make_item()
    second_item = DataItem(
        **{
            **first_item.__dict__,
            "id": "item-2",
            "source_id": r"C:\\second.txt",
            "name": "second.txt",
        }
    )
    retrieval = RecordingRetrieval(
        [
            RetrievalResult(item=first_item),
            RetrievalResult(item=second_item),
        ]
    )

    class FailsOnSecondRead:
        def __init__(self):
            self.calls = 0

        def read(self, item: DataItem) -> str | None:
            self.calls += 1
            if self.calls == 2:
                raise RuntimeError("second read failed")
            return "first document content"

    session = ConversationSession()
    agent = Agent(
        LLMIntegration(runtime),
        retrieval=retrieval,
        content_access=FailsOnSecondRead(),
    )

    with pytest.raises(RuntimeError, match="second read failed"):
        agent.run("summarize documents", session)

    assert runtime.request is None
    assert not any(
        message.role == "system" and "Retrieved context:" in message.content
        for message in session.get_messages()
    )

def test_agent_does_not_mutate_session_when_content_access_fails():
    runtime = RecordingRuntime()
    first_item = make_item()
    second_item = DataItem(
        **{
            **first_item.__dict__,
            "id": "item-2",
            "source_id": r"C:\\second.txt",
            "name": "second.txt",
        }
    )
    retrieval = RecordingRetrieval(
        [
            RetrievalResult(item=first_item),
            RetrievalResult(item=second_item),
        ]
    )

    class FailsOnSecondRead:
        def __init__(self):
            self.calls = 0

        def read(self, item: DataItem) -> str | None:
            self.calls += 1
            if self.calls == 2:
                raise RuntimeError("second read failed")
            return "first document content"

    session = ConversationSession()
    original_messages = session.get_messages()
    agent = Agent(
        LLMIntegration(runtime),
        retrieval=retrieval,
        content_access=FailsOnSecondRead(),
    )

    with pytest.raises(RuntimeError, match="second read failed"):
        agent.run("summarize documents", session)

    assert session.get_messages() == original_messages
    assert runtime.request is None



def test_retrieved_context_does_not_leak_into_next_turn():
    runtime = RecordingRuntime()
    item = make_item()
    retrieved_text = "PRIVATE_REFERENCE_CONTEXT_2026"
    retrieval = RecordingRetrieval([RetrievalResult(item=item)])
    content_access = RecordingContentAccess(
        {"item-1": retrieved_text}
    )
    session = ConversationSession()

    agent = Agent(
        LLMIntegration(runtime),
        retrieval=retrieval,
        content_access=content_access,
    )

    assert agent.run("First question", session) == "ok"
    assert runtime.request is not None
    first_request = runtime.request
    assert any(
        retrieved_text in message.content
        for message in first_request.messages
    )

    # The next turn has no retrieval results.
    retrieval.results = []
    assert agent.run("Second question", session) == "ok"

    assert runtime.request is not None
    second_request = runtime.request
    assert not any(
        retrieved_text in message.content
        for message in second_request.messages
    )
    assert not any(
        retrieved_text in message.content
        for message in session.get_messages()
    )
