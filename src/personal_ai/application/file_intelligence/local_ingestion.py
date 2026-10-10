from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from personal_ai.core.models import DataItem
from personal_ai.file_intelligence.index import ContentIndex
from personal_ai.file_intelligence.integration import (
    integrate_normalized_content,
)
from personal_ai.file_intelligence.normalization import NormalizedContent
from personal_ai.file_intelligence.orchestration import (
    FileIntelligenceOrchestrator,
)


@dataclass(frozen=True)
class ApplicationIngestionResult:
    """Canonical application ingestion result."""

    item: DataItem
    normalized: NormalizedContent


class LocalFileApplicationIngestion:
    """Application boundary for canonical local-file ingestion."""

    def __init__(
        self,
        *,
        orchestrator: FileIntelligenceOrchestrator,
        content_index: ContentIndex,
    ) -> None:
        self._orchestrator = orchestrator
        self._content_index = content_index

    def ingest(
        self,
        item: DataItem,
        *,
        mime_type: str | None,
        extension: str | None,
    ) -> ApplicationIngestionResult:
        if item.source != "local_filesystem":
            raise ValueError(
                "DataItem source must be local_filesystem"
            )

        result = self._orchestrator.process(
            source_path=item.source_id,
            mime_type=mime_type,
            extension=extension,
        )

        content_ref = (
            f"index://content/{result.normalized.content_hash}"
        )

        indexed_at = datetime.now(UTC).isoformat()

        integrated_item = integrate_normalized_content(
            item,
            result.normalized,
            self._content_index,
            content_ref=content_ref,
            indexed_at=indexed_at,
        )

        return ApplicationIngestionResult(
            item=integrated_item,
            normalized=result.normalized,
        )
