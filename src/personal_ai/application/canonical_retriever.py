from __future__ import annotations

from dataclasses import dataclass

from personal_ai.application.file_intelligence import (
    LocalFileApplicationIngestion,
)
from personal_ai.connectors.local_file_source import discover_enabled_local_files
from personal_ai.connectors.local_filesystem import local_file_to_data_item
from personal_ai.core.models import AccessPolicy
from personal_ai.file_intelligence.authorization import AuthorizationGate
from personal_ai.file_intelligence.extractors import (
    ExtractorRegistry,
    TextFileExtractor,
)
from personal_ai.file_intelligence.index import ContentIndex
from personal_ai.file_intelligence.orchestration import (
    FileIntelligenceOrchestrator,
)
from personal_ai.filesystem.scope import FilesystemAccessScope
from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.retrieval.local import (
    RetrievalRequest,
    RetrievalResult,
    retrieve_local_items,
)
from personal_ai.retrieval.local_search import (
    LocalSearchRequest,
    SearchableContent,
    search_local_content,
)
from personal_ai.sources.config import SourceConfig


@dataclass
class LocalCanonicalRetrieval:
    """Canonical application retrieval capability for local files."""

    filesystem_scope: FilesystemAccessScope
    source_config: SourceConfig
    permission_evaluator: PermissionEvaluator
    content_index: ContentIndex | None = None

    def __post_init__(self) -> None:
        registry = ExtractorRegistry()
        registry.register(TextFileExtractor())

        authorization_gate = AuthorizationGate(
            filesystem_scope=self.filesystem_scope,
            permission_evaluator=self.permission_evaluator,
        )

        orchestrator = FileIntelligenceOrchestrator(
            extractor_registry=registry,
            authorization_gate=authorization_gate,
        )

        if self.content_index is None:
            self.content_index = ContentIndex()

        self._ingestion = LocalFileApplicationIngestion(
            orchestrator=orchestrator,
            content_index=self.content_index,
        )

    def retrieve(
        self,
        request: RetrievalRequest,
    ) -> list[RetrievalResult]:
        if not request.query.strip():
            raise ValueError("Retrieval query must not be empty")

        if request.limit <= 0:
            raise ValueError("Retrieval limit must be greater than zero")

        if not self.filesystem_scope.authorized_roots:
            return []

        if not self.source_config.is_enabled("local_filesystem"):
            return []

        if (
            self.permission_evaluator.evaluate(
                "local_filesystem",
                "read",
            )
            != "allowed"
        ):
            return []

        searchable_contents: list[SearchableContent] = []

        for root in self.filesystem_scope.authorized_roots:
            metadata_items = discover_enabled_local_files(
                root,
                self.source_config,
            )

            for metadata in metadata_items:
                if not self.filesystem_scope.is_allowed(metadata.path):
                    continue

                item = local_file_to_data_item(metadata)
                item.access_policy = AccessPolicy(
                    read=True,
                    write=False,
                )

                result = self._ingestion.ingest(
                    item,
                    mime_type=metadata.mime_type,
                    extension=metadata.path.suffix,
                )

                searchable_contents.append(
                    SearchableContent(
                        item=result.item,
                        text=result.normalized.text,
                    )
                )

        results = search_local_content(
            searchable_contents,
            LocalSearchRequest(query=request.query),
        )

        result_ids = {result.item.id for result in results}

        canonical_items = [
            searchable.item
            for searchable in searchable_contents
            if searchable.item.id in result_ids
        ]

        return retrieve_local_items(
            canonical_items,
            request,
        )
