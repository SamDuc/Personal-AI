import hashlib
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

from personal_ai.file_intelligence.consistency import (
    SourceSnapshot,
    snapshot_local_file,
)
from personal_ai.file_intelligence.consistency_resolver import (
    CONSISTENT,
    OUT_OF_SYNC,
    SOURCE_MISSING,
    SOURCE_UNAVAILABLE,
    ConsistencyResolver,
)
from personal_ai.file_intelligence.index import IndexedContent


def _indexed(path: Path) -> IndexedContent:
    return IndexedContent(
        source_path=str(path),
        content_hash=(
            hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
            if path.is_file()
            else "sha256:test"
        ),
        content_ref="content:test",
        indexed_at=datetime.now(UTC).isoformat(),
        searchable=True,
        sync_status="indexed",
    )


def test_consistent_when_source_snapshot_matches(tmp_path: Path):
    source = tmp_path / "sample.txt"
    source.write_text("hello", encoding="utf-8")

    snapshot = snapshot_local_file(source)

    result = ConsistencyResolver().resolve(
        _indexed(source),
        indexed_source_modified_at=snapshot.modified_at,
    )

    assert result.state == CONSISTENT
    assert result.source_snapshot == snapshot


def test_out_of_sync_when_source_modified_at_differs(tmp_path: Path):
    source = tmp_path / "sample.txt"
    source.write_text("hello", encoding="utf-8")

    snapshot = snapshot_local_file(source)

    result = ConsistencyResolver().resolve(
        _indexed(source),
        indexed_source_modified_at=snapshot.modified_at - timedelta(seconds=1),
    )

    assert result.state == OUT_OF_SYNC
    assert result.source_snapshot == snapshot



def test_out_of_sync_when_content_changes_but_mtime_is_preserved(
    tmp_path: Path,
):
    source = tmp_path / "sample.txt"
    source.write_text("original content", encoding="utf-8")
    original_snapshot = snapshot_local_file(source)

    indexed = _indexed(source)
    source.write_text("changed content", encoding="utf-8")
    os.utime(
        source,
        ns=(source.stat().st_atime_ns, original_snapshot.modified_at_ns),
    )

    result = ConsistencyResolver().resolve(
        indexed,
        indexed_source_modified_at=original_snapshot.modified_at,
    )

    assert result.state == OUT_OF_SYNC
    assert result.source_snapshot is not None
    assert result.source_snapshot.content_hash != indexed.content_hash

def test_source_missing(tmp_path: Path):
    source = tmp_path / "missing.txt"

    result = ConsistencyResolver().resolve(
        _indexed(source),
        indexed_source_modified_at=datetime.now(UTC),
    )

    assert result.state == SOURCE_MISSING
    assert result.source_snapshot is None


def test_source_unavailable():
    source = Path("unavailable.txt")

    def unavailable(_: str | Path) -> SourceSnapshot:
        raise PermissionError("access denied")

    result = ConsistencyResolver(
        snapshotter=unavailable,
    ).resolve(
        _indexed(source),
        indexed_source_modified_at=datetime.now(UTC),
    )

    assert result.state == SOURCE_UNAVAILABLE
    assert result.source_snapshot is None


def test_resolver_is_observational(tmp_path: Path):
    source = tmp_path / "sample.txt"
    original = "hello"
    source.write_text(original, encoding="utf-8")

    indexed = _indexed(source)

    snapshot = SourceSnapshot(
        source="local_filesystem",
        source_id=str(source.resolve()),
        modified_at=datetime.fromtimestamp(
            source.stat().st_mtime,
            tz=UTC,
        ),
    )

    result = ConsistencyResolver().resolve(
        indexed,
        indexed_source_modified_at=snapshot.modified_at,
    )

    assert result.state == CONSISTENT
    assert source.read_text(encoding="utf-8") == original
    assert indexed.sync_status == "indexed"
    assert indexed.content_hash == hashlib.sha256(original.encode("utf-8")).hexdigest()


def test_resolver_does_not_refresh_or_reindex(tmp_path: Path):
    source = tmp_path / "sample.txt"
    source.write_text("hello", encoding="utf-8")

    indexed = _indexed(source)
    original_indexed_at = indexed.indexed_at

    snapshot = SourceSnapshot(
        source="local_filesystem",
        source_id=str(source.resolve()),
        modified_at=datetime.fromtimestamp(
            source.stat().st_mtime,
            tz=UTC,
        ),
    )

    result = ConsistencyResolver().resolve(
        indexed,
        indexed_source_modified_at=snapshot.modified_at,
    )

    assert result.state == CONSISTENT
    assert indexed.indexed_at == original_indexed_at



def test_snapshot_does_not_decode_non_text_files(tmp_path: Path):
    source = tmp_path / "sample.bin"
    source.write_bytes(bytes([0xFF, 0x00, 0xFE]))

    snapshot = snapshot_local_file(source)

    assert snapshot.source_id == str(source.resolve())
    assert snapshot.content_hash is None


def test_invalid_utf8_text_is_source_unavailable(tmp_path: Path):
    source = tmp_path / "invalid.txt"
    source.write_bytes(bytes([0xFF, 0xFE]))

    indexed = IndexedContent(
        source_path=str(source),
        content_hash="previous-indexed-hash",
        content_ref="content:previous",
        indexed_at=datetime.now(UTC).isoformat(),
        searchable=True,
        sync_status="indexed",
    )

    result = ConsistencyResolver().resolve(
        indexed,
        indexed_source_modified_at=datetime.fromtimestamp(
            source.stat().st_mtime,
            tz=UTC,
        ),
    )

    assert result.state == SOURCE_UNAVAILABLE
    assert result.source_snapshot is None
