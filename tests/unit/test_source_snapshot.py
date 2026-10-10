from datetime import UTC
from pathlib import Path

import pytest

from personal_ai.file_intelligence.consistency import (
    SourceSnapshot,
    snapshot_local_file,
)


def test_snapshot_local_file_captures_authoritative_source_metadata(
    tmp_path: Path,
):
    source = tmp_path / "notes.txt"
    source.write_text("hello", encoding="utf-8")

    snapshot = snapshot_local_file(source)

    assert isinstance(snapshot, SourceSnapshot)
    assert snapshot.source == "local_filesystem"
    assert snapshot.source_id == str(source.resolve())
    assert snapshot.modified_at.tzinfo == UTC

    stat = source.stat()
    assert abs(snapshot.modified_at.timestamp() - stat.st_mtime) < 1


def test_snapshot_rejects_missing_source(tmp_path: Path):
    source = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError):
        snapshot_local_file(source)


def test_snapshot_rejects_directory(tmp_path: Path):
    with pytest.raises(ValueError, match="regular file"):
        snapshot_local_file(tmp_path)
