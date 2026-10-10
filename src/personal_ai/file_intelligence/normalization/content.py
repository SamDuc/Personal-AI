"""Canonical normalization for extracted file content."""

from dataclasses import dataclass


@dataclass(frozen=True)
class NormalizedContent:
    """Canonical representation of extracted textual content."""

    source_path: str
    text: str
    content_hash: str
    content_type: str
    normalization_version: str


def normalize_extracted_content(
    *,
    source_path: str,
    text: str,
    content_hash: str,
    extraction_format: str,
    extraction_version: str,
) -> NormalizedContent:
    """Normalize extracted content without performing extraction."""
    if not source_path:
        raise ValueError("source_path must not be empty")

    if not content_hash:
        raise ValueError("content_hash must not be empty")

    if not extraction_format:
        raise ValueError("extraction_format must not be empty")

    if not extraction_version:
        raise ValueError("extraction_version must not be empty")

    return NormalizedContent(
        source_path=source_path,
        text=text,
        content_hash=content_hash,
        content_type=extraction_format,
        normalization_version="1",
    )
