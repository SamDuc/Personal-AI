from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from personal_ai.core.models import AccessPolicy, DataItem


@dataclass(frozen=True)
class LocalFileMetadata:
    path: Path
    size: int | None = None
    created_at: datetime | None = None
    modified_at: datetime | None = None
    mime_type: str | None = None


def _file_uri(path: Path) -> str:
    return path.resolve().as_uri()


def local_file_to_data_item(metadata: LocalFileMetadata) -> DataItem:
    """Map local filesystem metadata to the canonical DataItem model."""
    path = metadata.path

    return DataItem(
        id=f"local:{path.resolve()}",
        source="local_filesystem",
        source_id=str(path.resolve()),
        uri=_file_uri(path),
        item_type="file",
        mime_type=metadata.mime_type,
        extension=path.suffix or None,
        name=path.name,
        size=metadata.size,
        created_at=metadata.created_at,
        modified_at=metadata.modified_at,
        content_available=False,
        content_ref=None,
        content_hash=None,
        searchable=False,
        embedding_ref=None,
        indexed_at=None,
        source_modified_at=metadata.modified_at,
        sync_status="new",
        access_policy=AccessPolicy(read=False, write=False),
        sensitivity="normal",
    )
