from pathlib import Path

from personal_ai.connectors.local_content_index import index_extracted_content
from personal_ai.connectors.local_file_content_extraction import ExtractedContent
from personal_ai.core.models import DataItem


def integrate_local_content_index(
    item: DataItem,
    extracted: ExtractedContent,
) -> DataItem:
    if item.source != "local_filesystem":
        raise ValueError("DataItem source must be local_filesystem")

    item_path = Path(item.source_id).resolve()
    extracted_path = extracted.path.resolve()

    if item_path != extracted_path:
        raise ValueError("Extracted content does not match DataItem source")

    index = index_extracted_content(extracted)

    item.content_available = index.content_available
    item.content_ref = index.content_ref
    item.content_hash = index.content_hash
    item.searchable = index.searchable
    item.indexed_at = index.indexed_at
    item.sync_status = index.sync_status

    return item
