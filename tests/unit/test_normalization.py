import pytest

from personal_ai.file_intelligence.normalization import (
    NormalizedContent,
    normalize_extracted_content,
)


def test_normalization_returns_canonical_content() -> None:
    result = normalize_extracted_content(
        source_path="example.txt",
        text="hello world",
        content_hash="abc123",
        extraction_format="text/plain",
        extraction_version="1",
    )

    assert isinstance(result, NormalizedContent)
    assert result.source_path == "example.txt"
    assert result.text == "hello world"
    assert result.content_hash == "abc123"
    assert result.content_type == "text/plain"
    assert result.normalization_version == "1"


def test_normalization_preserves_content_hash() -> None:
    result = normalize_extracted_content(
        source_path="example.txt",
        text="content",
        content_hash="stable-hash",
        extraction_format="text/plain",
        extraction_version="1",
    )

    assert result.content_hash == "stable-hash"


def test_normalization_rejects_missing_source() -> None:
    with pytest.raises(ValueError, match="source_path"):
        normalize_extracted_content(
            source_path="",
            text="content",
            content_hash="hash",
            extraction_format="text/plain",
            extraction_version="1",
        )


def test_normalization_rejects_missing_hash() -> None:
    with pytest.raises(ValueError, match="content_hash"):
        normalize_extracted_content(
            source_path="example.txt",
            text="content",
            content_hash="",
            extraction_format="text/plain",
            extraction_version="1",
        )


def test_normalization_rejects_missing_extraction_format() -> None:
    with pytest.raises(ValueError, match="extraction_format"):
        normalize_extracted_content(
            source_path="example.txt",
            text="content",
            content_hash="hash",
            extraction_format="",
            extraction_version="1",
        )


def test_normalization_rejects_missing_extraction_version() -> None:
    with pytest.raises(ValueError, match="extraction_version"):
        normalize_extracted_content(
            source_path="example.txt",
            text="content",
            content_hash="hash",
            extraction_format="text/plain",
            extraction_version="",
        )
