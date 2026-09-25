from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256

from personal_ai.connectors.local_file_content_extraction import ExtractedContent


@dataclass(frozen=True)
class LocalContentIndex:
    content_ref: str
    content_hash: str
    content_available: bool
    searchable: bool
    embedding_ref: str | None
    indexed_at: datetime
    sync_status: str


def index_extracted_content(extracted: ExtractedContent) -> LocalContentIndex:
    if not extracted.content_available:
        raise ValueError("Extracted content is unavailable")

    content_key = sha256(
        extracted.text.encode("utf-8")
    ).hexdigest()

    content_ref = f"index://content/local-{content_key}"

    return LocalContentIndex(
        content_ref=content_ref,
        content_hash=extracted.content_hash,
        content_available=True,
        searchable=True,
        embedding_ref=None,
        indexed_at=datetime.now(UTC),
        sync_status="indexed",
    )
