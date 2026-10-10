from __future__ import annotations

from dataclasses import dataclass, field

from personal_ai.connectors.local_file_source import discover_enabled_local_files
from personal_ai.connectors.local_filesystem import local_file_to_data_item
from personal_ai.core.models import AccessPolicy, DataItem
from personal_ai.file_intelligence.authorization import AuthorizationGate
from personal_ai.file_intelligence.consistency_resolver import (
    CONSISTENT,
    ConsistencyResolver,
)
from personal_ai.file_intelligence.extractors import (
    ExtractorRegistry,
    TextFileExtractor,
)
from personal_ai.file_intelligence.index import ContentIndex
from personal_ai.file_intelligence.orchestration import (
    FileIntelligenceOrchestrator,
)
from personal_ai.file_intelligence.refresh import LocalFileRefresh
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
    """Canonical retrieval over explicitly refreshed local-file content."""

    filesystem_scope: FilesystemAccessScope
    source_config: SourceConfig
    permission_evaluator: PermissionEvaluator
    content_index: ContentIndex | None = None
    _catalog: dict[str, DataItem] = field(
        default_factory=dict,
        init=False,
        repr=False,
    )

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

        self._refresh_service = LocalFileRefresh(
            orchestrator=orchestrator,
            content_index=self.content_index,
        )
        self._consistency_resolver = ConsistencyResolver()

    def refresh(self) -> int:
        """Explicitly discover and refresh authorized local files."""
        if not self.filesystem_scope.authorized_roots:
            return 0
        if not self.source_config.is_enabled("local_filesystem"):
            return 0
        if (
            self.permission_evaluator.evaluate(
                "local_filesystem",
                "read",
            )
            != "allowed"
        ):
            return 0

        refreshed: dict[str, DataItem] = {}
        previous_states = {}

        try:
            for root in self.filesystem_scope.authorized_roots:
                metadata_items = discover_enabled_local_files(
                    root,
                    self.source_config,
                )
                for metadata in metadata_items:
                    if not self.filesystem_scope.is_allowed(metadata.path):
                        continue

                    item = local_file_to_data_item(metadata)
                    item.access_policy = AccessPolicy(read=True, write=False)

                    source_path = item.source_id
                    if source_path not in previous_states:
                        previous_states[source_path] = (
                            self.content_index.capture_source_state(source_path)
                        )

                    result = self._refresh_service.refresh(
                        item,
                        mime_type=metadata.mime_type,
                        extension=metadata.path.suffix,
                    )
                    refreshed[result.item.id] = result.item
        except Exception as refresh_error:
            rollback_errors = []

            for source_path, state in reversed(list(previous_states.items())):
                try:
                    self.content_index.restore_source_state(state)
                except Exception as rollback_error:  # noqa: BLE001
                    rollback_errors.append(rollback_error)

            if rollback_errors:
                self._catalog = {}
                raise ExceptionGroup(
                    "Batch refresh failed and index rollback also failed",
                    [refresh_error, *rollback_errors],
                ) from None

            raise

        self._catalog = refreshed
        return len(refreshed)

    def retrieve(
        self,
        request: RetrievalRequest,
    ) -> list[RetrievalResult]:
        """Search indexed content without discovery, ingestion, or mutation."""
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
        if self.content_index is None:
            return []

        searchable_contents: list[SearchableContent] = []

        for item in tuple(self._catalog.values()):
            if item.source != "local_filesystem":
                continue
            if not self.filesystem_scope.is_allowed(item.source_id):
                continue
            if not item.content_available or not item.searchable:
                continue
            if item.content_ref is None or item.content_hash is None:
                continue
            if item.source_modified_at is None or not item.access_policy.read:
                continue

            indexed = self.content_index.get(item.source_id)
            if indexed is None:
                continue
            if indexed.sync_status != "indexed":
                continue
            if indexed.content_ref != item.content_ref:
                continue
            if indexed.content_hash != item.content_hash:
                continue

            consistency = self._consistency_resolver.resolve(
                indexed,
                indexed_source_modified_at=item.source_modified_at,
            )
            if consistency.state != CONSISTENT:
                continue

            text = self.content_index.get_content(
                item.content_ref,
                source_path=item.source_id,
                content_hash=item.content_hash,
            )
            if text is None:
                continue

            searchable_contents.append(
                SearchableContent(item=item, text=text)
            )

        results = search_local_content(
            searchable_contents,
            LocalSearchRequest(
                query=request.query,
                limit=request.limit,
            ),
        )
        result_ids = {result.item.id for result in results}
        canonical_items = [
            searchable.item
            for searchable in searchable_contents
            if searchable.item.id in result_ids
        ]

        return retrieve_local_items(canonical_items, request)
