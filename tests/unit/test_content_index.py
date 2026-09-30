from personal_ai.file_intelligence.index import ContentIndex, IndexedContent
from personal_ai.file_intelligence.normalization import (
    normalize_extracted_content,
)


def make_content():
    return normalize_extracted_content(
        source_path="example.txt",
        text="hello world",
        content_hash="abc123",
        extraction_format="text/plain",
        extraction_version="1",
    )


def test_index_creates_derived_representation() -> None:
    index = ContentIndex()
    content = make_content()

    result = index.index(
        content,
        content_ref="local://example.txt",
        indexed_at="2026-09-30T19:00:00+07:00",
    )

    assert isinstance(result, IndexedContent)
    assert result.source_path == "example.txt"
    assert result.content_hash == "abc123"
    assert result.content_ref == "local://example.txt"
    assert result.searchable is True
    assert result.sync_status == "indexed"


def test_index_can_resolve_stored_representation() -> None:
    index = ContentIndex()
    content = make_content()

    index.index(
        content,
        content_ref="local://example.txt",
        indexed_at="2026-09-30T19:00:00+07:00",
    )

    result = index.get("example.txt")

    assert result is not None
    assert result.content_hash == "abc123"


def test_index_returns_none_for_unknown_source() -> None:
    index = ContentIndex()

    assert index.get("missing.txt") is None


def test_index_rejects_missing_content_ref() -> None:
    index = ContentIndex()
    content = make_content()

    try:
        index.index(
            content,
            content_ref="",
            indexed_at="2026-09-30T19:00:00+07:00",
        )
    except ValueError as exc:
        assert str(exc) == "content_ref must not be empty"
    else:
        raise AssertionError("ValueError was not raised")


def test_index_rejects_missing_indexed_at() -> None:
    index = ContentIndex()
    content = make_content()

    try:
        index.index(
            content,
            content_ref="local://example.txt",
            indexed_at="",
        )
    except ValueError as exc:
        assert str(exc) == "indexed_at must not be empty"
    else:
        raise AssertionError("ValueError was not raised")
