from dataclasses import dataclass

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


@dataclass
class RecordingRetrieval:
    requests: list[RetrievalRequest]
    results: list[RetrievalResult]

    def retrieve(self, request: RetrievalRequest) -> list[RetrievalResult]:
        self.requests.append(request)
        return list(self.results)


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
        size=10,
        content_available=True,
        content_ref="index://content/abc",
        content_hash="abc",
        searchable=True,
        sync_status="indexed",
    )


def test_agent_requests_canonical_retrieval():
    runtime = RecordingRuntime()
    retrieval = RecordingRetrieval(
        requests=[],
        results=[],
    )

    agent = Agent(
        LLMIntegration(runtime),
        retrieval=retrieval,
    )

    session = ConversationSession()

    result = agent.run(
        "find Raspberry Pi architecture",
        session,
    )

    assert result == "ok"
    assert retrieval.requests == [
        RetrievalRequest(
            query="find Raspberry Pi architecture",
        )
    ]


def test_agent_receives_canonical_retrieval_results():
    runtime = RecordingRuntime()
    item = make_item()

    retrieval = RecordingRetrieval(
        requests=[],
        results=[RetrievalResult(item=item)],
    )

    agent = Agent(
        LLMIntegration(runtime),
        retrieval=retrieval,
    )

    session = ConversationSession()

    result = agent.run("notes", session)

    assert result == "ok"
    assert retrieval.requests == [
        RetrievalRequest(query="notes"),
    ]
    assert runtime.request is not None
    assert item.source == "local_filesystem"
    assert item.content_ref == "index://content/abc"
    assert item.sync_status == "indexed"


def test_agent_propagates_canonical_retrieval_failure():
    runtime = RecordingRuntime()

    class FailingRetrieval:
        def retrieve(self, request: RetrievalRequest) -> list[RetrievalResult]:
            raise RuntimeError("canonical retrieval failed")

    agent = Agent(
        LLMIntegration(runtime),
        retrieval=FailingRetrieval(),
    )

    session = ConversationSession()

    with pytest.raises(
        RuntimeError,
        match="canonical retrieval failed",
    ):
        agent.run("find notes", session)

    assert runtime.request is None


def test_agent_does_not_mutate_item_access_policy():
    runtime = RecordingRuntime()
    item = make_item()
    item.access_policy.read = True
    item.access_policy.write = False

    original_policy = (
        item.access_policy.read,
        item.access_policy.write,
    )

    retrieval = RecordingRetrieval(
        requests=[],
        results=[RetrievalResult(item=item)],
    )

    agent = Agent(
        LLMIntegration(runtime),
        retrieval=retrieval,
    )

    agent.run("find notes", ConversationSession())

    assert (
        item.access_policy.read,
        item.access_policy.write,
    ) == original_policy
def test_agent_rejects_both_canonical_and_legacy_retrievers():
    runtime = RecordingRuntime()

    class LegacyRetriever:
        def __call__(self, query: str) -> list[str]:
            return ["legacy content"]

    retrieval = RecordingRetrieval(
        requests=[],
        results=[],
    )

    with pytest.raises(
        ValueError,
        match="cannot configure both canonical and legacy retrieval",
    ):
        Agent(
            LLMIntegration(runtime),
            retriever=LegacyRetriever(),
            retrieval=retrieval,
        )
