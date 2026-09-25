from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AccessPolicy:
    read: bool = False
    write: bool = False


@dataclass
class DataItem:
    id: str
    source: str
    source_id: str
    uri: str

    item_type: str
    mime_type: str | None = None
    extension: str | None = None

    name: str | None = None
    size: int | None = None
    created_at: datetime | None = None
    modified_at: datetime | None = None

    content_available: bool = False
    content_ref: str | None = None
    content_hash: str | None = None

    project: str | None = None
    topics: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    searchable: bool = False
    embedding_ref: str | None = None

    indexed_at: datetime | None = None
    source_modified_at: datetime | None = None
    sync_status: str = "new"

    access_policy: AccessPolicy = field(default_factory=AccessPolicy)
    sensitivity: str = "normal"