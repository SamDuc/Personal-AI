from pathlib import Path

import pytest

from personal_ai.connectors.local_file_content_extraction import extract_local_file_content


def test_extract_plain_text_file(tmp_path: Path) -> None:
    source = tmp_path / "notes.txt"
    source.write_text("Hello Personal AI\nThis is a test.", encoding="utf-8")

    result = extract_local_file_content(source)

    assert result.path == source
    assert result.text == "Hello Personal AI\nThis is a test."
    assert result.content_available is True
    assert result.content_hash
    assert result.extraction_version == "1"


def test_extract_same_content_produces_same_hash(tmp_path: Path) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    content = "same content"
    first.write_text(content, encoding="utf-8")
    second.write_text(content, encoding="utf-8")

    first_result = extract_local_file_content(first)
    second_result = extract_local_file_content(second)

    assert first_result.text == second_result.text
    assert first_result.content_hash == second_result.content_hash


def test_missing_file_raises_file_not_found(tmp_path: Path) -> None:
    source = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError):
        extract_local_file_content(source)


def test_directory_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(IsADirectoryError):
        extract_local_file_content(tmp_path)


def test_unsupported_file_type_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "data.bin"
    source.write_bytes(b"binary-data")

    with pytest.raises(ValueError, match="Unsupported"):
        extract_local_file_content(source)


def test_invalid_utf8_text_raises_extraction_error(tmp_path: Path) -> None:
    source = tmp_path / "invalid.txt"
    source.write_bytes(b"valid-prefix\xffinvalid")

    with pytest.raises(ValueError, match="decode"):
        extract_local_file_content(source)
