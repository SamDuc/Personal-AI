from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from personal_ai.connectors.local_file_source import (
    discover_enabled_local_files,
)
from personal_ai.connectors.local_filesystem import local_file_to_data_item
from personal_ai.core.models import AccessPolicy
from personal_ai.file_intelligence.capability import resolve_file_capability
from personal_ai.file_intelligence.extractors import (
    ExtractedContent,
    ExtractorRegistry,
)
from personal_ai.file_intelligence.index import ContentIndex
from personal_ai.file_intelligence.normalization import (
    normalize_extracted_content,
)
from personal_ai.retrieval.local import (
    RetrievalRequest,
    retrieve_local_items,
)
from personal_ai.sources.config import SourceConfig


@dataclass(frozen=True)
class TextExtractor:
    extractor_type: str = "text"

    def extract(self, source_path: str) -> ExtractedContent:
        path = Path(source_path)
        text = path.read_text(encoding="utf-8")
        content_hash = sha256(text.encode("utf-8")).hexdigest()

        return ExtractedContent(
            source_path=source_path,
            text=text,
            content_hash=content_hash,
            extraction_format="text",
            extraction_version="1",
        )


def test_b06_local_file_full_intelligence_pipeline(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text(
        "Raspberry Pi personal AI architecture",
        encoding="utf-8",
    )

    config = SourceConfig(
        {
            "sources": {
                "local_filesystem": {
                    "enabled": True,
                }
            }
        }
    )

    # Discovery
    discovered = discover_enabled_local_files(tmp_path, config)

    assert len(discovered) == 1
    metadata = discovered[0]
    assert metadata.path.resolve() == path.resolve()

    # Canonical DataItem
    item = local_file_to_data_item(metadata)

    assert item.source == "local_filesystem"
    assert item.source_id == str(path.resolve())
    assert item.content_available is False
    assert item.searchable is False

    # Authorization is established before extraction.
    item.access_policy = AccessPolicy(
        read=True,
        write=False,
    )

    # Capability resolution
    capability = resolve_file_capability(
        mime_type=metadata.mime_type or "text/plain",
        extension=path.suffix,
    )

    assert capability.extraction_supported is True
    assert capability.extractor_type == "text"

    # Extractor registry
    registry = ExtractorRegistry()
    registry.register(TextExtractor())

    extractor = registry.get(capability.extractor_type)

    assert extractor is not None

    # Extraction through the resolved extractor
    extracted = extractor.extract(str(path))

    assert extracted.source_path == str(path)
    assert extracted.text == (
        "Raspberry Pi personal AI architecture"
    )
    assert extracted.content_hash
    assert extracted.extraction_format == "text"
    assert extracted.extraction_version == "1"

    # Normalization
    normalized = normalize_extracted_content(
        source_path=extracted.source_path,
        text=extracted.text,
        content_hash=extracted.content_hash,
        extraction_format=extracted.extraction_format,
        extraction_version=extracted.extraction_version,
    )

    assert Path(normalized.source_path).resolve() == path.resolve()
    assert normalized.text == extracted.text
    assert normalized.content_hash == extracted.content_hash
    assert normalized.content_type == "text"
    assert normalized.normalization_version == "1"

    # Content index
    content_index = ContentIndex()

    indexed = content_index.index(
        normalized,
        content_ref=f"index://content/{normalized.content_hash}",
        indexed_at="2026-09-30T00:00:00+00:00",
    )

    assert Path(indexed.source_path).resolve() == path.resolve()
    assert indexed.content_hash == normalized.content_hash
    assert indexed.searchable is True
    assert indexed.sync_status == "indexed"

    # Canonical DataItem receives derived index state.
    item.content_available = True
    item.content_ref = indexed.content_ref
    item.content_hash = indexed.content_hash
    item.searchable = indexed.searchable
    item.indexed_at = indexed.indexed_at
    item.sync_status = indexed.sync_status

    # Retrieval must not alter authorization.
    policy_before = item.access_policy

    results = retrieve_local_items(
        [item],
        RetrievalRequest(
            query="Raspberry Pi personal AI architecture",
            source="local_filesystem",
            limit=10,
        ),
    )

    assert len(results) == 1
    assert results[0].item.id == item.id
    assert results[0].item.content_ref == indexed.content_ref
    assert results[0].item.content_hash == normalized.content_hash
    assert item.access_policy is policy_before
    assert item.access_policy == AccessPolicy(
        read=True,
        write=False,
    )


def test_b06_unsupported_capability_stops_before_extraction() -> None:
    capability = resolve_file_capability(
        mime_type="application/pdf",
        extension=".pdf",
    )

    assert capability.extraction_supported is False
    assert capability.extractor_type is None
