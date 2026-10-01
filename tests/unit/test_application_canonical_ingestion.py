from dataclasses import dataclass
from pathlib import Path

import pytest

from personal_ai.application.file_intelligence import (
    LocalFileApplicationIngestion,
)
from personal_ai.core.models import AccessPolicy, DataItem
from personal_ai.file_intelligence.authorization import AuthorizationGate
from personal_ai.file_intelligence.extractors import (
    ExtractedContent,
    ExtractorRegistry,
)
from personal_ai.file_intelligence.index import ContentIndex
from personal_ai.file_intelligence.orchestration import (
    FileIntelligenceOrchestrator,
)
from personal_ai.filesystem.scope import FilesystemAccessScope
from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.permissions.policy import PermissionPolicy


@dataclass
class FakeTextExtractor:
    extractor_type: str = "text"

    def extract(self, source_path: str) -> ExtractedContent:
        path = Path(source_path)

        return ExtractedContent(
            source_path=str(path.resolve()),
            text=path.read_text(encoding="utf-8"),
            content_hash="application-canonical-hash",
            extraction_format="text",
            extraction_version="1",
        )


def make_ingestion(tmp_path: Path) -> LocalFileApplicationIngestion:
    registry = ExtractorRegistry()
    registry.register(FakeTextExtractor())

    permissions = PermissionEvaluator(
        PermissionPolicy(
            {
                "defaults": {
                    "local_filesystem": {
                        "read": True,
                    },
                },
                "confirmation_required": [],
            }
        )
    )

    scope = FilesystemAccessScope([tmp_path])

    gate = AuthorizationGate(
        filesystem_scope=scope,
        permission_evaluator=permissions,
    )

    orchestrator = FileIntelligenceOrchestrator(
        extractor_registry=registry,
        authorization_gate=gate,
    )

    return LocalFileApplicationIngestion(
        orchestrator=orchestrator,
        content_index=ContentIndex(),
    )


def make_item(path: Path) -> DataItem:
    return DataItem(
        id=f"local:{path.resolve()}",
        source="local_filesystem",
        source_id=str(path.resolve()),
        uri=path.resolve().as_uri(),
        item_type="file",
        mime_type="text/plain",
        extension=".txt",
        name=path.name,
        size=path.stat().st_size,
        access_policy=AccessPolicy(
            read=True,
            write=False,
        ),
    )


def test_application_ingestion_uses_canonical_pipeline(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text(
        "Application uses canonical file intelligence.",
        encoding="utf-8",
    )

    item = make_item(path)
    ingestion = make_ingestion(tmp_path)

    result = ingestion.ingest(
        item,
        mime_type="text/plain",
        extension=".txt",
    )

    assert result.item is item
    assert result.item.content_available is True
    assert result.item.content_ref is not None
    assert result.item.content_hash == "application-canonical-hash"
    assert result.item.searchable is True
    assert result.item.sync_status == "indexed"
    assert result.normalized.text == (
        "Application uses canonical file intelligence."
    )
    assert result.item.access_policy.read is True
    assert result.item.indexed_at


def test_application_ingestion_preserves_dataitem_access_policy(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("protected application content", encoding="utf-8")

    item = make_item(path)
    original_policy = item.access_policy
    ingestion = make_ingestion(tmp_path)

    result = ingestion.ingest(
        item,
        mime_type="text/plain",
        extension=".txt",
    )

    assert result.item.access_policy == original_policy
    assert result.item.access_policy.read is True
    assert result.item.access_policy.write is False


def test_application_ingestion_rejects_non_local_source(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("content", encoding="utf-8")

    item = make_item(path)
    item.source = "remote"

    ingestion = make_ingestion(tmp_path)

    with pytest.raises(ValueError, match="local_filesystem"):
        ingestion.ingest(
            item,
            mime_type="text/plain",
            extension=".txt",
        )
