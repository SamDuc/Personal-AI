from pathlib import Path

from personal_ai.connectors.local_content_index import index_extracted_content
from personal_ai.retrieval.local_integration import integrate_local_content_index
from personal_ai.connectors.local_file_content_extraction import (
    extract_local_file_content,
)
from personal_ai.connectors.local_file_source import discover_enabled_local_files
from personal_ai.connectors.local_filesystem import local_file_to_data_item
from personal_ai.core.agent import Agent
from personal_ai.core.conversation_session import ConversationSession
from personal_ai.core.llm import ChatMessage, LLMResponse
from personal_ai.core.llm_integration import LLMIntegration
from personal_ai.core.llm_runtime import LLMRuntime
from personal_ai.retrieval.local_search import (
    LocalSearchRequest,
    SearchableContent,
    search_local_content,
)
from personal_ai.sources.config import SourceConfig


class ContextAwareRuntime(LLMRuntime):
    def __init__(self) -> None:
        self.request_messages: list[ChatMessage] = []

    def generate(self, request):
        self.request_messages = list(request.messages)

        context = [
            message.content
            for message in request.messages
            if message.role == "system"
        ]

        return LLMResponse(
            text=f"Answer based on context: {context[-1]}",
        )


def test_real_file_agent_retrieval_llm_pipeline(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text(
        "Raspberry Pi personal AI architecture uses local retrieval.",
        encoding="utf-8",
    )

    config = SourceConfig(
        {
            "sources": {
                "local_filesystem": {
                    "enabled": True,
                }
            }
        }
    )

    discovered = discover_enabled_local_files(tmp_path, config)
    assert len(discovered) == 1

    item = local_file_to_data_item(discovered[0])
    item.access_policy.read = True

    extracted = extract_local_file_content(path)
    item = integrate_local_content_index(item, extracted)

    searchable = SearchableContent(
        item=item,
        text=extracted.text,
    )

    def retrieve(query: str) -> list[str]:
        results = search_local_content(
            [searchable],
            LocalSearchRequest(query=query),
        )
        return [
            searchable.text
            for result in results
            if result.item.content_ref == searchable.item.content_ref
        ]

    runtime = ContextAwareRuntime()
    integration = LLMIntegration(runtime)
    agent = Agent(integration, retriever=retrieve)
    session = ConversationSession()

    response = agent.run(
        "Raspberry Pi personal AI architecture",
        session,
    )

    assert item.source == "local_filesystem"
    assert response.startswith("Answer based on context:")
    assert "Raspberry Pi personal AI architecture" in response
    assert any(
        message.role == "system"
        and "local retrieval" in message.content
        for message in runtime.request_messages
    )
    assert session.messages[0] == ChatMessage(
        role="user",
        content="Raspberry Pi personal AI architecture",
    )
    assert session.messages[-1].role == "assistant"
