from pathlib import Path

from personal_ai.connectors.local_content_index import index_extracted_content
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
from personal_ai.filesystem.scope import FilesystemAccessScope
from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.permissions.policy import PermissionPolicy
from personal_ai.retrieval.local_integration import integrate_local_content_index
from personal_ai.retrieval.local_search import (
    LocalSearchRequest,
    SearchableContent,
    search_local_content,
)
from personal_ai.sources.config import SourceConfig
from personal_ai.tools.executor import ToolExecutor
from personal_ai.tools.local_file_read import LocalFileReadTool


def make_evaluator(read: bool) -> PermissionEvaluator:
    return PermissionEvaluator(
        PermissionPolicy(
            {
                "defaults": {
                    "local_filesystem": {
                        "read": read,
                    }
                },
                "confirmation_required": [],
            }
        )
    )


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


def test_local_file_retrieval_agent_tool_end_to_end(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    content = (
        "Raspberry Pi personal AI architecture uses local retrieval "
        "and authorized local file tools."
    )
    path.write_text(content, encoding="utf-8")

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
    assert item.source == "local_filesystem"
    assert item.content_ref is None

    extracted = extract_local_file_content(path)
    assert extracted.content_available is True
    assert extracted.text == content

    item = integrate_local_content_index(item, extracted)
    item.access_policy.read = True
    assert item.content_available is True
    assert item.content_ref is not None
    assert item.searchable is True

    indexed = index_extracted_content(extracted)
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

    retrieved = retrieve("Raspberry Pi personal AI")
    assert retrieved == [content]

    runtime = ContextAwareRuntime()
    integration = LLMIntegration(runtime)
    agent = Agent(integration, retriever=retrieve)
    session = ConversationSession()

    response = agent.run(
        "Raspberry Pi personal AI",
        session,
    )

    assert response.startswith("Answer based on context:")
    assert content in response
    assert any(
        message.role == "system"
        and content in message.content
        for message in runtime.request_messages
    )

    tool = LocalFileReadTool(
        filesystem_scope=FilesystemAccessScope([tmp_path]),
    )
    executor = ToolExecutor()
    evaluator = make_evaluator(read=True)

    result = agent.execute_tool(
        tool=tool,
        executor=executor,
        input_data=str(path),
        permission_evaluator=evaluator,
    )

    assert result.status == "success"
    assert result.result == content
