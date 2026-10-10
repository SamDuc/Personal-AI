import hashlib
from pathlib import Path

import pytest

from personal_ai.file_intelligence.extractors import TextFileExtractor


def test_text_extractor_reads_utf8_and_hashes_content(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    text = "Xin chào Personal AI.\nCanonical text extraction."

    path.write_text(text, encoding="utf-8")

    result = TextFileExtractor().extract(str(path))

    assert result.source_path == str(path.resolve())
    assert result.text == text
    assert result.content_hash == hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()
    assert result.extraction_format == "text"
    assert result.extraction_version == "1"


def test_text_extractor_rejects_missing_file(
    tmp_path: Path,
) -> None:
    path = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError):
        TextFileExtractor().extract(str(path))


def test_text_extractor_rejects_directory(
    tmp_path: Path,
) -> None:
    with pytest.raises(IsADirectoryError):
        TextFileExtractor().extract(str(tmp_path))


def test_text_extractor_rejects_unsupported_extension(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.md"
    path.write_text("content", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported file type"):
        TextFileExtractor().extract(str(path))


def test_text_extractor_rejects_invalid_utf8(
    tmp_path: Path,
) -> None:
    path = tmp_path / "invalid.txt"
    path.write_bytes(b"\xff\xfe\xfd")

    with pytest.raises(ValueError, match="Unable to decode"):
        TextFileExtractor().extract(str(path))
