from personal_ai.core.models import AccessPolicy, DataItem
from personal_ai.file_intelligence.index import ContentIndex
from personal_ai.file_intelligence.integration.dataitem import (
    integrate_normalized_content,
)
from personal_ai.file_intelligence.normalization import NormalizedContent


def make_item() -> DataItem:
    return DataItem(
        id="local:C:/workspace/notes.txt",
        source="local_filesystem",
        source_id="C:/workspace/notes.txt",
        uri="file:///C:/workspace/notes.txt",
        item_type="file",
        mime_type="text/plain",
        extension=".txt",
        name="notes.txt",
        size=5,
        access_policy=AccessPolicy(read=True, write=False),
        sensitivity="normal",
    )


def make_content() -> NormalizedContent:
    return NormalizedContent(
        source_path="C:/workspace/notes.txt",
        text="hello",
        content_hash="abc123",
        content_type="text",
        normalization_version="1",
    )


def test_integrate_normalized_content_populates_dataitem():
    item = make_item()
    content = make_content()
    index = ContentIndex()

    result = integrate_normalized_content(
        item,
        content,
        index,
        content_ref="index://content/abc123",
        indexed_at="2026-09-30T00:00:00Z",
    )

    assert result is item
    assert result.content_available is True
    assert result.content_ref == "index://content/abc123"
    assert result.content_hash == "abc123"
    assert result.searchable is True
    assert result.indexed_at == "2026-09-30T00:00:00Z"
    assert result.sync_status == "indexed"

    assert result.embedding_ref is None
    assert result.access_policy.read is True
    assert result.access_policy.write is False
    assert result.sensitivity == "normal"


def test_integrate_preserves_canonical_identity():
    item = make_item()
    content = make_content()
    index = ContentIndex()

    integrate_normalized_content(
        item,
        content,
        index,
        content_ref="index://content/abc123",
        indexed_at="2026-09-30T00:00:00Z",
    )

    assert item.id == "local:C:/workspace/notes.txt"
    assert item.source == "local_filesystem"
    assert item.source_id == "C:/workspace/notes.txt"
    assert item.uri == "file:///C:/workspace/notes.txt"
    assert item.item_type == "file"
    assert item.mime_type == "text/plain"
    assert item.extension == ".txt"
    assert item.name == "notes.txt"


def test_integrate_rejects_source_mismatch():
    item = make_item()
    content = NormalizedContent(
        source_path="C:/workspace/other.txt",
        text="hello",
        content_hash="abc123",
        content_type="text",
        normalization_version="1",
    )
    index = ContentIndex()

    try:
        integrate_normalized_content(
            item,
            content,
            index,
            content_ref="index://content/abc123",
            indexed_at="2026-09-30T00:00:00Z",
        )
    except ValueError as exc:
        assert "does not match" in str(exc)
    else:
        raise AssertionError("Expected ValueError for source mismatch")


def test_integrated_content_is_available_from_content_index():
    item = make_item()
    content = make_content()
    index = ContentIndex()

    integrate_normalized_content(
        item,
        content,
        index,
        content_ref="index://content/abc123",
        indexed_at="2026-09-30T00:00:00Z",
    )

    indexed = index.get("C:/workspace/notes.txt")

    assert indexed is not None
    assert indexed.source_path == "C:/workspace/notes.txt"
    assert indexed.content_hash == "abc123"
    assert indexed.content_ref == "index://content/abc123"
    assert indexed.searchable is True
    assert indexed.sync_status == "indexed"
