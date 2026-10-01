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
        """Refresh one local-file representation explicitly."""
        if item.source != "local_filesystem":
            raise ValueError(
                "DataItem source must be local_filesystem"
            )

        result = self._orchestrator.process(
            source_path=item.source_id,
            mime_type=mime_type,
            extension=extension,
        )

        source_snapshot = snapshot_local_file(item.source_id)

        content_ref = (
            f"index://content/{result.normalized.content_hash}"
        )
        indexed_at = datetime.now(UTC).isoformat()

        indexed = self._content_index.index(
            result.normalized,
            content_ref=content_ref,
            indexed_at=indexed_at,
        )

        item.content_available = indexed.searchable
        item.content_ref = indexed.content_ref
        item.content_hash = indexed.content_hash
        item.searchable = indexed.searchable
        item.indexed_at = indexed.indexed_at
        item.source_modified_at = source_snapshot.modified_at
        item.sync_status = indexed.sync_status

        return RefreshResult(
            item=item,
            source_snapshot=source_snapshot,
        )
