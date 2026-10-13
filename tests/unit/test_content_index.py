from dataclasses import replace

import pytest

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
def test_index_resolves_content_by_reference_and_source():
    index = ContentIndex()
    content = make_content()

    index.index(
        content,
        content_ref="local://example.txt",
        indexed_at="2026-09-30T19:00:00+07:00",
    )

    assert (
        index.get_content(
            "local://example.txt",
            source_path="example.txt",
            content_hash=content.content_hash,
        )
        == "hello world"
    )


def test_index_does_not_resolve_content_for_wrong_source():
    index = ContentIndex()
    content = make_content()

    index.index(
        content,
        content_ref="local://example.txt",
        indexed_at="2026-09-30T19:00:00+07:00",
    )

    assert (
        index.get_content(
            "local://example.txt",
            source_path="other.txt",
            content_hash=content.content_hash,
        )
        is None
    )


def test_index_returns_none_for_unknown_content_reference():
    index = ContentIndex()

    assert (
        index.get_content(
            "local://missing.txt",
            source_path="missing.txt",
            content_hash="missing-hash",
        )
        is None
    )
def test_index_keeps_content_references_isolated_by_source():
    index = ContentIndex()

    first = normalize_extracted_content(
        source_path="first.txt",
        text="first document",
        content_hash="hash-first",
        extraction_format="text/plain",
        extraction_version="1",
    )
    second = normalize_extracted_content(
        source_path="second.txt",
        text="second document",
        content_hash="hash-second",
        extraction_format="text/plain",
        extraction_version="1",
    )

    index.index(
        first,
        content_ref="index://content/shared",
        indexed_at="2026-10-01T00:00:00+00:00",
    )
    index.index(
        second,
        content_ref="index://content/shared",
        indexed_at="2026-10-01T00:01:00+00:00",
    )

    assert (
        index.get_content(
            "index://content/shared",
            source_path="first.txt",
            content_hash=first.content_hash,
        )
        == "first document"
    )
    assert (
        index.get_content(
            "index://content/shared",
            source_path="second.txt",
            content_hash=second.content_hash,
        )
        == "second document"
    )


def test_index_rejects_content_hash_mismatch():
    index = ContentIndex()
    content = make_content()

    index.index(
        content,
        content_ref="local://example.txt",
        indexed_at="2026-10-01T00:00:00+00:00",
    )

    assert (
        index.get_content(
            "local://example.txt",
            source_path=content.source_path,
            content_hash="wrong-hash",
        )
        is None
    )


def test_reindex_replaces_current_content_for_same_source():
    index = ContentIndex()
    first = normalize_extracted_content(
        source_path="example.txt",
        text="old content",
        content_hash="hash-old",
        extraction_format="text/plain",
        extraction_version="1",
    )
    second = normalize_extracted_content(
        source_path="example.txt",
        text="new content",
        content_hash="hash-new",
        extraction_format="text/plain",
        extraction_version="1",
    )

    index.index(
        first,
        content_ref="local://example.txt",
        indexed_at="2026-10-01T00:00:00+00:00",
    )
    index.index(
        second,
        content_ref="local://example.txt",
        indexed_at="2026-10-01T00:01:00+00:00",
    )

    assert (
        index.get_content(
            "local://example.txt",
            source_path="example.txt",
            content_hash="hash-old",
        )
        is None
    )
    assert (
        index.get_content(
            "local://example.txt",
            source_path="example.txt",
            content_hash="hash-new",
        )
        == "new content"
    )


def test_index_rejects_blank_content_hash():
    index = ContentIndex()
    content = replace(make_content(), content_hash="   ")

    with pytest.raises(ValueError, match="content_hash must not be empty"):
        index.index(
            content,
            content_ref="index://content/test",
            indexed_at="2026-10-13T00:00:00Z",
        )
