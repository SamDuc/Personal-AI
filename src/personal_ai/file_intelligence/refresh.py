"""Explicit refresh boundary for local indexed file content."""

from dataclasses import dataclass
from datetime import UTC, datetime

from personal_ai.core.models import DataItem
from personal_ai.file_intelligence.consistency import (
    SourceSnapshot,
    snapshot_local_file,
)
from personal_ai.file_intelligence.index import ContentIndex
from personal_ai.file_intelligence.orchestration import (
    FileIntelligenceOrchestrator,
)


@dataclass(frozen=True)
class RefreshResult:
    """Result produced by an explicit local-file refresh."""

    item: DataItem
    source_snapshot: SourceSnapshot


class LocalFileRefresh:
    """Explicitly refresh one authorized local-file representation."""

    def __init__(
        self,
        *,
        orchestrator: FileIntelligenceOrchestrator,
        content_index: ContentIndex,
    ) -> None:
        self._orchestrator = orchestrator
        self._content_index = content_index

    def refresh(
        self,
        item: DataItem,
        *,
        mime_type: str | None,
        extension: str | None,
    ) -> RefreshResult:
        """Refresh one source while holding its shared index lock."""
        if item.source != "local_filesystem":
            raise ValueError("DataItem source must be local_filesystem")

        with self._content_index.lock_source(item.source_id):
            return self._refresh_locked(
                item,
                mime_type=mime_type,
                extension=extension,
            )

    def _refresh_locked(
        self,
        item: DataItem,
        *,
        mime_type: str | None,
        extension: str | None,
    ) -> RefreshResult:
        result = self._orchestrator.process(
            source_path=item.source_id,
            mime_type=mime_type,
            extension=extension,
        )

        source_snapshot = snapshot_local_file(item.source_id)
        if source_snapshot != result.source_snapshot:
            raise RuntimeError(
                "Source file changed after extraction and before indexing: "
                f"{item.source_id}"
            )

        content_ref = f"index://content/{result.normalized.content_hash}"
        indexed_at = datetime.now(UTC).isoformat()
        source_path = result.normalized.source_path
        index_state = self._content_index.capture_source_state(source_path)

        try:
            indexed = self._content_index.index(
                result.normalized,
                content_ref=content_ref,
                indexed_at=indexed_at,
            )
            source_snapshot_after_index = snapshot_local_file(item.source_id)
            if source_snapshot_after_index != result.source_snapshot:
                raise RuntimeError(
                    "Source file changed during indexing: "
                    f"{item.source_id}"
                )
        except Exception as refresh_error:
            try:
                self._content_index.restore_source_state(index_state)
            except Exception as rollback_error:
                raise ExceptionGroup(
                    "Refresh failed and index rollback also failed",
                    [refresh_error, rollback_error],
                ) from None
            raise

        item.content_available = indexed.searchable
        item.content_ref = indexed.content_ref
        item.content_hash = indexed.content_hash
        item.searchable = indexed.searchable
        item.indexed_at = indexed.indexed_at
        item.source_modified_at = source_snapshot_after_index.modified_at
        item.sync_status = indexed.sync_status

        return RefreshResult(
            item=item,
            source_snapshot=source_snapshot_after_index,
        )
