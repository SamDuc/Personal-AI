"""Canonical DataItem and content-index integration."""

from pathlib import Path

from personal_ai.core.models import DataItem
from personal_ai.file_intelligence.index import ContentIndex
from personal_ai.file_intelligence.normalization import NormalizedContent


def integrate_normalized_content(
    item: DataItem,
    content: NormalizedContent,
    index: ContentIndex,
    *,
    content_ref: str,
    indexed_at: str,
) -> DataItem:
    """Index normalized content and apply the resulting state to DataItem."""
    if item.source != "local_filesystem":
        raise ValueError("DataItem source must be local_filesystem")

    item_path = Path(item.source_id).resolve()
    content_path = Path(content.source_path).resolve()

    if item_path != content_path:
        raise ValueError("Normalized content does not match DataItem source")

    indexed = index.index(
        content,
        content_ref=content_ref,
        indexed_at=indexed_at,
    )

    item.content_available = True
    item.content_ref = indexed.content_ref
    item.content_hash = indexed.content_hash
    item.searchable = indexed.searchable
    item.indexed_at = indexed.indexed_at
    item.sync_status = indexed.sync_status

    return item
