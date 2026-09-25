from datetime import UTC, datetime
from pathlib import Path

from personal_ai.connectors.local_filesystem import (
    LocalFileMetadata,
    local_file_to_data_item,
)


def test_local_file_to_data_item_maps_basic_identity():
    metadata = LocalFileMetadata(
        path=Path(r"C:\Projects\paper.pdf"),
        size=123456,
        mime_type="application/pdf",
    )

    item = local_file_to_data_item(metadata)

    assert item.id == r"local:C:\Projects\paper.pdf"
    assert item.source == "local_filesystem"
    assert item.source_id == r"C:\Projects\paper.pdf"
    assert item.uri == "file:///C:/Projects/paper.pdf"
    assert item.item_type == "file"
    assert item.name == "paper.pdf"
    assert item.extension == ".pdf"
    assert item.size == 123456
    assert item.mime_type == "application/pdf"


def test_local_file_to_data_item_maps_timestamps_and_sync_state():
    timestamp = datetime(2026, 9, 25, 12, 30, tzinfo=UTC)

    metadata = LocalFileMetadata(
        path=Path(r"C:\Projects\paper.pdf"),
        modified_at=timestamp,
        created_at=timestamp,
    )

    item = local_file_to_data_item(metadata)

    assert item.created_at == timestamp
    assert item.modified_at == timestamp
    assert item.source_modified_at == timestamp
    assert item.sync_status == "new"


def test_local_file_mapping_starts_read_only_and_not_searchable():
    metadata = LocalFileMetadata(
        path=Path(r"C:\Projects\paper.pdf"),
    )

    item = local_file_to_data_item(metadata)

    assert item.access_policy.read is True
    assert item.access_policy.write is False
    assert item.content_available is False
    assert item.content_ref is None
    assert item.content_hash is None
    assert item.searchable is False
    assert item.embedding_ref is None


def test_local_file_mapping_handles_files_without_extension():
    metadata = LocalFileMetadata(
        path=Path(r"C:\Projects\README"),
    )

    item = local_file_to_data_item(metadata)

    assert item.name == "README"
    assert item.extension is None
