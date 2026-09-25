from pathlib import Path

import pytest

from personal_ai.connectors.local_file_discovery import discover_local_files
from personal_ai.connectors.local_filesystem import LocalFileMetadata


def test_discover_local_files_returns_files_in_scope(tmp_path: Path):
    file_a = tmp_path / "paper.pdf"
    file_b = tmp_path / "notes.txt"

    file_a.write_bytes(b"pdf-content")
    file_b.write_text("text-content", encoding="utf-8")

    result = discover_local_files(tmp_path)

    paths = {item.path for item in result}

    assert paths == {file_a, file_b}
    assert all(isinstance(item, LocalFileMetadata) for item in result)


def test_discover_local_files_is_recursive(tmp_path: Path):
    nested = tmp_path / "project" / "docs"
    nested.mkdir(parents=True)

    file_a = tmp_path / "root.txt"
    file_b = nested / "paper.pdf"

    file_a.write_text("root", encoding="utf-8")
    file_b.write_bytes(b"pdf")

    result = discover_local_files(tmp_path)

    paths = {item.path for item in result}

    assert paths == {file_a, file_b}


def test_discover_local_files_does_not_return_directories(tmp_path: Path):
    directory = tmp_path / "docs"
    directory.mkdir()

    file_a = directory / "paper.pdf"
    file_a.write_bytes(b"pdf")

    result = discover_local_files(tmp_path)

    assert all(item.path.is_file() for item in result)
    assert all(item.path != directory for item in result)


def test_discover_local_files_rejects_missing_scope(tmp_path: Path):
    missing = tmp_path / "does-not-exist"

    with pytest.raises(FileNotFoundError):
        discover_local_files(missing)


def test_discover_local_files_rejects_file_scope(tmp_path: Path):
    file_scope = tmp_path / "paper.pdf"
    file_scope.write_bytes(b"pdf")

    with pytest.raises(NotADirectoryError):
        discover_local_files(file_scope)
def test_discover_local_files_collects_filesystem_metadata(tmp_path: Path):
    file_a = tmp_path / "paper.pdf"
    file_a.write_bytes(b"pdf-content")

    result = discover_local_files(tmp_path)

    assert len(result) == 1

    metadata = result[0]

    assert metadata.path == file_a
    assert metadata.size == len(b"pdf-content")
    assert metadata.modified_at is not None
    assert metadata.created_at is not None
    assert metadata.mime_type == "application/pdf"