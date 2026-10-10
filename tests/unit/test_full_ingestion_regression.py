from pathlib import Path

import pytest

from personal_ai.connectors.local_file_source import (
    discover_enabled_local_files,
)
from personal_ai.connectors.local_filesystem import local_file_to_data_item
from personal_ai.core.models import AccessPolicy
from personal_ai.file_intelligence.extractors import (
    ExtractedContent,
    ExtractorRegistry,
)
from personal_ai.file_intelligence.index import ContentIndex
from personal_ai.file_intelligence.integration import (
    integrate_normalized_content,
)
from personal_ai.file_intelligence.orchestration import (
    FileIntelligenceOrchestrator,
)
from personal_ai.file_intelligence.orchestration.pipeline import (
    AuthorizationGate,
)
from personal_ai.filesystem.scope import FilesystemAccessScope
from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.permissions.policy import PermissionPolicy
from personal_ai.retrieval.local import (
    RetrievalRequest,
    retrieve_local_items,
)
from personal_ai.sources.config import SourceConfig


class FakeTextExtractor:
    extractor_type = "text"

    def __init__(self) -> None:
        self.called = False

    def extract(self, source_path: str) -> ExtractedContent:
        self.called = True

        path = Path(source_path)
        text = path.read_text(encoding="utf-8")

        return ExtractedContent(
            source_path=str(path.resolve()),
            text=text,
            content_hash="full-ingestion-hash",
            extraction_format="text",
            extraction_version="1",
        )


def make_source_config(enabled: bool = True) -> SourceConfig:
    return SourceConfig(
        {
            "sources": {
                "local_filesystem": {
                    "enabled": enabled,
                }
            }
        }
    )


def make_permission_evaluator(read: bool = True) -> PermissionEvaluator:
    return PermissionEvaluator(
        PermissionPolicy(
            {
                "defaults": {
                    "local_filesystem": {
                        "read": read,
                    },
                },
                "confirmation_required": [],
            }
        )
    )


def make_orchestrator(
    *,
    scope: FilesystemAccessScope,
    permission_evaluator: PermissionEvaluator,
):
    registry = ExtractorRegistry()
    extractor = FakeTextExtractor()
    registry.register(extractor)

    authorization_gate = AuthorizationGate(
        filesystem_scope=scope,
        permission_evaluator=permission_evaluator,
    )

    orchestrator = FileIntelligenceOrchestrator(
        extractor_registry=registry,
        authorization_gate=authorization_gate,
    )

    return orchestrator, extractor


def test_full_ingestion_pipeline_reaches_retrieval(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text(
        "Personal AI canonical ingestion pipeline",
        encoding="utf-8",
    )

    source_config = make_source_config()
    scope = FilesystemAccessScope([tmp_path])
    permissions = make_permission_evaluator()

    discovered = discover_enabled_local_files(
        tmp_path,
        source_config,
    )

    assert len(discovered) == 1
    assert discovered[0].path == path

    item = local_file_to_data_item(discovered[0])

    assert item.source == "local_filesystem"
    assert item.content_available is False
    assert item.searchable is False

    item.access_policy = AccessPolicy(
        read=True,
        write=False,
    )

    orchestrator, extractor = make_orchestrator(
        scope=scope,
        permission_evaluator=permissions,
    )

    result = orchestrator.process(
        source_path=path,
        mime_type="text/plain",
        extension=".txt",
    )

    assert extractor.called is True
    assert result.capability.extraction_supported is True
    assert result.capability.extractor_type == "text"
    assert "canonical ingestion" in result.extracted.text
    assert result.normalized.text == result.extracted.text

    index = ContentIndex()

    item = integrate_normalized_content(
        item,
        result.normalized,
        index,
        content_ref="index://content/full-ingestion-hash",
        indexed_at="2026-10-01T00:00:00Z",
    )

    assert item.content_available is True
    assert item.searchable is True
    assert item.content_ref == "index://content/full-ingestion-hash"
    assert item.content_hash == "full-ingestion-hash"
    assert item.sync_status == "indexed"

    indexed = index.get(str(path.resolve()))

    assert indexed is not None
    assert indexed.content_hash == item.content_hash
    assert indexed.content_ref == item.content_ref

    results = retrieve_local_items(
        [item],
        RetrievalRequest(
            query="canonical ingestion",
            source="local_filesystem",
            limit=10,
        ),
    )

    assert len(results) == 1
    assert results[0].item.id == item.id


def test_source_disabled_stops_before_ingestion(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("disabled source", encoding="utf-8")

    source_config = make_source_config(enabled=False)

    discovered = discover_enabled_local_files(
        tmp_path,
        source_config,
    )

    assert discovered == []


def test_scope_denied_stops_before_extraction(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("scope denied", encoding="utf-8")

    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir()

    scope = FilesystemAccessScope([allowed_root])
    permissions = make_permission_evaluator()

    orchestrator, extractor = make_orchestrator(
        scope=scope,
        permission_evaluator=permissions,
    )

    with pytest.raises(PermissionError, match="filesystem_scope_denied"):
        orchestrator.process(
            source_path=path,
            mime_type="text/plain",
            extension=".txt",
        )

    assert extractor.called is False


def test_permission_denied_stops_before_extraction(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("permission denied", encoding="utf-8")

    scope = FilesystemAccessScope([tmp_path])
    permissions = make_permission_evaluator(read=False)

    orchestrator, extractor = make_orchestrator(
        scope=scope,
        permission_evaluator=permissions,
    )

    with pytest.raises(PermissionError, match="permission_denied"):
        orchestrator.process(
            source_path=path,
            mime_type="text/plain",
            extension=".txt",
        )

    assert extractor.called is False


def test_unsupported_capability_stops_before_extraction(
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.pdf"
    path.write_bytes(b"%PDF-test")

    scope = FilesystemAccessScope([tmp_path])
    permissions = make_permission_evaluator()

    orchestrator, extractor = make_orchestrator(
        scope=scope,
        permission_evaluator=permissions,
    )

    with pytest.raises(ValueError, match="Unsupported file capability"):
        orchestrator.process(
            source_path=path,
            mime_type="application/pdf",
            extension=".pdf",
        )

    assert extractor.called is False
