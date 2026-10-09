from datetime import UTC, datetime
from pathlib import Path

import pytest

from personal_ai.core.models import DataItem
from personal_ai.file_intelligence.authorization import AuthorizationGate
from personal_ai.file_intelligence.consistency import (
    snapshot_local_file,
)
from personal_ai.file_intelligence.extractors.registry import (
    ExtractedContent,
    ExtractorRegistry,
)
from personal_ai.file_intelligence.index import ContentIndex
from personal_ai.file_intelligence.orchestration import (
    FileIntelligenceOrchestrator,
)
from personal_ai.file_intelligence.refresh import (
    LocalFileRefresh,
)
from personal_ai.filesystem.scope import FilesystemAccessScope
from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.permissions.policy import PermissionPolicy


class FakeTextExtractor:
    extractor_type = "text"

    def __init__(self) -> None:
        self.called = False

    def extract(self, source_path: str) -> ExtractedContent:
        self.called = True
        return ExtractedContent(
            source_path=source_path,
            text="hello personal ai",
            content_hash="abc123",
            extraction_format="text",
            extraction_version="1",
        )


def make_item(path: Path) -> DataItem:
    resolved = str(path.resolve())
    return DataItem(
        id=f"local:{resolved}",
        source="local_filesystem",
        source_id=resolved,
        uri=resolved,
        item_type="file",
        mime_type="text/plain",
        extension=".txt",
        name=path.name,
        size=path.stat().st_size,
        created_at=datetime.now(UTC),
        modified_at=datetime.fromtimestamp(
            path.stat().st_mtime,
            tz=UTC,
        ),
    )


def make_refresh(
    root: Path,
    *,
    read: bool = True,
) -> tuple[LocalFileRefresh, FakeTextExtractor, ContentIndex]:
    extractor = FakeTextExtractor()

    registry = ExtractorRegistry()
    registry.register(extractor)

    policy = PermissionPolicy(
        {
            "defaults": {
                "local_filesystem": {
                    "read": read,
                    "write": False,
                },
            },
            "confirmation_required": [],
        }
    )

    gate = AuthorizationGate(
        filesystem_scope=FilesystemAccessScope([root]),
        permission_evaluator=PermissionEvaluator(policy),
    )

    orchestrator = FileIntelligenceOrchestrator(
        registry,
        gate,
    )
    content_index = ContentIndex()

    refresh = LocalFileRefresh(
        orchestrator=orchestrator,
        content_index=content_index,
    )

    return refresh, extractor, content_index


def test_refresh_indexes_normalized_content(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    item = make_item(path)
    refresh, extractor, index = make_refresh(tmp_path)

    result = refresh.refresh(
        item,
        mime_type="text/plain",
        extension=".txt",
    )

    indexed = index.get(str(path.resolve()))

    assert extractor.called is True
    assert result.item is item
    assert result.item.content_available is True
    assert result.item.searchable is True
    assert result.item.content_hash == "abc123"
    assert result.item.content_ref == "index://content/abc123"
    assert result.item.sync_status == "indexed"
    assert indexed is not None
    assert indexed.content_hash == "abc123"
    assert indexed.searchable is True
    assert indexed.sync_status == "indexed"


def test_refresh_associates_current_source_snapshot(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    item = make_item(path)
    refresh, _, _ = make_refresh(tmp_path)

    result = refresh.refresh(
        item,
        mime_type="text/plain",
        extension=".txt",
    )

    expected = snapshot_local_file(path)

    assert result.source_snapshot.source == "local_filesystem"
    assert result.source_snapshot.source_id == str(path.resolve())
    assert result.item.source_modified_at == expected.modified_at


def test_refresh_records_index_and_source_timestamps_separately(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    item = make_item(path)
    refresh, _, index = make_refresh(tmp_path)

    result = refresh.refresh(
        item,
        mime_type="text/plain",
        extension=".txt",
    )

    indexed = index.get(str(path.resolve()))

    assert indexed is not None
    assert result.item.indexed_at == indexed.indexed_at
    assert result.item.source_modified_at == result.source_snapshot.modified_at

    indexed_at = datetime.fromisoformat(result.item.indexed_at)
    assert indexed_at.tzinfo is not None
    assert indexed_at.utcoffset() is not None

def test_refresh_rejects_non_local_source(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    item = make_item(path)
    item.source = "remote"

    refresh, _, _ = make_refresh(tmp_path)

    with pytest.raises(ValueError, match="local_filesystem"):
        refresh.refresh(
            item,
            mime_type="text/plain",
            extension=".txt",
        )


def test_refresh_propagates_authorization_failure(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    item = make_item(path)
    refresh, extractor, _ = make_refresh(
        tmp_path,
        read=False,
    )

    with pytest.raises(
        PermissionError,
        match="permission_denied",
    ):
        refresh.refresh(
            item,
            mime_type="text/plain",
            extension=".txt",
        )

    assert extractor.called is False


def test_refresh_propagates_unsupported_capability(
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.pdf"
    path.write_bytes(b"%PDF")

    item = make_item(path)
    refresh, extractor, _ = make_refresh(tmp_path)

    with pytest.raises(
        ValueError,
        match="Unsupported file capability",
    ):
        refresh.refresh(
            item,
            mime_type="application/pdf",
            extension=".pdf",
        )

    assert extractor.called is False


def test_refresh_propagates_missing_source(
    tmp_path: Path,
) -> None:
    path = tmp_path / "missing.txt"

    item = DataItem(
        id=f"local:{path.resolve()}",
        source="local_filesystem",
        source_id=str(path.resolve()),
        uri=str(path.resolve()),
        item_type="file",
        mime_type="text/plain",
        extension=".txt",
        name=path.name,
        size=0,
        created_at=datetime.now(UTC),
        modified_at=datetime.now(UTC),
    )

    refresh, _, _ = make_refresh(tmp_path)

    with pytest.raises(FileNotFoundError):
        refresh.refresh(
            item,
            mime_type="text/plain",
            extension=".txt",
        )


def test_refresh_does_not_modify_source_content(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    original = "hello"
    path.write_text(original, encoding="utf-8")

    item = make_item(path)
    refresh, _, _ = make_refresh(tmp_path)

    refresh.refresh(
        item,
        mime_type="text/plain",
        extension=".txt",
    )

    assert path.read_text(encoding="utf-8") == original


def test_refresh_requires_explicit_invocation(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    item = make_item(path)
    refresh, extractor, index = make_refresh(tmp_path)

    assert extractor.called is False
    assert index.get(str(path.resolve())) is None
    assert item.content_available is False

    refresh.refresh(
        item,
        mime_type="text/plain",
        extension=".txt",
    )

    assert extractor.called is True
    assert index.get(str(path.resolve())) is not None


def test_refresh_does_not_use_legacy_orchestration_path(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    item = make_item(path)
    refresh, _, index = make_refresh(tmp_path)

    result = refresh.refresh(
        item,
        mime_type="text/plain",
        extension=".txt",
    )

    indexed = index.get(str(path.resolve()))

    assert result.item.content_ref == "index://content/abc123"
    assert indexed is not None
    assert indexed.content_ref == "index://content/abc123"
