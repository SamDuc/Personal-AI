from datetime import UTC, datetime
from pathlib import Path

from personal_ai.file_intelligence.consistency import SourceSnapshot
from personal_ai.file_intelligence.consistency_resolver import (
    SOURCE_MISSING,
    SOURCE_UNAVAILABLE,
    ConsistencyResolver,
)
from personal_ai.file_intelligence.index import IndexedContent


def make_indexed(path: Path) -> IndexedContent:
    return IndexedContent(
        source_path=str(path),
        content_hash="sha256:test",
        content_ref="content:test",
        indexed_at=datetime.now(UTC).isoformat(),
        searchable=True,
        sync_status="indexed",
    )


def test_missing_authoritative_source_is_not_current(
    tmp_path: Path,
) -> None:
    source = tmp_path / "missing.txt"
    indexed = make_indexed(source)

    result = ConsistencyResolver().resolve(
        indexed,
        indexed_source_modified_at=datetime.now(UTC),
    )

    assert result.state == SOURCE_MISSING
    assert result.source_snapshot is None
    assert indexed.sync_status == "indexed"
    assert indexed.searchable is True


def test_unavailable_authoritative_source_is_not_current() -> None:
    source = Path("unavailable.txt")
    indexed = make_indexed(source)

    def unavailable(_: str | Path) -> SourceSnapshot:
        raise PermissionError("access denied")

    result = ConsistencyResolver(
        snapshotter=unavailable,
    ).resolve(
        indexed,
        indexed_source_modified_at=datetime.now(UTC),
    )

    assert result.state == SOURCE_UNAVAILABLE
    assert result.source_snapshot is None
    assert indexed.sync_status == "indexed"
    assert indexed.searchable is True


def test_missing_source_does_not_modify_filesystem(
    tmp_path: Path,
) -> None:
    source = tmp_path / "missing.txt"
    indexed = make_indexed(source)

    result = ConsistencyResolver().resolve(
        indexed,
        indexed_source_modified_at=datetime.now(UTC),
    )

    assert result.state == SOURCE_MISSING
    assert not source.exists()


def test_unavailable_source_does_not_modify_indexed_representation() -> None:
    source = Path("unavailable.txt")
    indexed = make_indexed(source)

    original = (
        indexed.source_path,
        indexed.content_hash,
        indexed.content_ref,
        indexed.indexed_at,
        indexed.searchable,
        indexed.sync_status,
    )

    def unavailable(_: str | Path) -> SourceSnapshot:
        raise OSError("filesystem unavailable")

    result = ConsistencyResolver(
        snapshotter=unavailable,
    ).resolve(
        indexed,
        indexed_source_modified_at=datetime.now(UTC),
    )

    assert result.state == SOURCE_UNAVAILABLE
    assert (
        indexed.source_path,
        indexed.content_hash,
        indexed.content_ref,
        indexed.indexed_at,
        indexed.searchable,
        indexed.sync_status,
    ) == original
