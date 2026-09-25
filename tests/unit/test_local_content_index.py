from datetime import UTC
from pathlib import Path

import pytest

from personal_ai.connectors.local_content_index import (
    LocalContentIndex,
    index_extracted_content,
)
from personal_ai.connectors.local_file_content_extraction import (
    ExtractedContent,
)


def make_extracted_content(
    tmp_path: Path,
    text: str = "Hello Personal AI",
) -> ExtractedContent:
    source = tmp_path / "notes.txt"

    return ExtractedContent(
        path=source,
        text=text,
        content_hash="test-hash",
        content_available=True,
        extraction_version="1",
    )


def test_index_extracted_content_creates_index_record(tmp_path: Path) -> None:
    extracted = make_extracted_content(tmp_path)

    result = index_extracted_content(extracted)

    assert isinstance(result, LocalContentIndex)
    assert result.content_ref.startswith("index://content/")
    assert result.content_hash == "test-hash"
    assert result.content_available is True
    assert result.searchable is True
    assert result.embedding_ref is None
    assert result.sync_status == "indexed"
    assert result.indexed_at.tzinfo is not None


def test_index_preserves_extracted_content_hash(tmp_path: Path) -> None:
    extracted = make_extracted_content(tmp_path)

    result = index_extracted_content(extracted)

    assert result.content_hash == extracted.content_hash


def test_same_extracted_content_produces_same_content_ref(tmp_path: Path) -> None:
    first = make_extracted_content(tmp_path, "same content")
    second = make_extracted_content(tmp_path, "same content")

    first_result = index_extracted_content(first)
    second_result = index_extracted_content(second)

    assert first_result.content_ref == second_result.content_ref


def test_index_rejects_unavailable_content(tmp_path: Path) -> None:
    extracted = ExtractedContent(
        path=tmp_path / "notes.txt",
        text="",
        content_hash="test-hash",
        content_available=False,
        extraction_version="1",
    )

    with pytest.raises(ValueError, match="content"):
        index_extracted_content(extracted)


def test_index_does_not_create_embedding(tmp_path: Path) -> None:
    extracted = make_extracted_content(tmp_path)

    result = index_extracted_content(extracted)

    assert result.embedding_ref is None


def test_indexed_at_is_utc_aware(tmp_path: Path) -> None:
    extracted = make_extracted_content(tmp_path)

    result = index_extracted_content(extracted)

    assert result.indexed_at.tzinfo == UTC
