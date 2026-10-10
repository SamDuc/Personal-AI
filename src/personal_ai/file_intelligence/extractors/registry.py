"""Extractor contracts and registry."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ExtractedContent:
    """Content extracted from one explicitly selected file."""

    source_path: str
    text: str
    content_hash: str
    extraction_format: str
    extraction_version: str


class FileExtractor(Protocol):
    """Protocol implemented by concrete file extractors."""

    extractor_type: str

    def extract(self, source_path: str) -> ExtractedContent:
        """Extract content from the selected source file."""


class ExtractorRegistry:
    """Resolve an extractor by its declared extractor type."""

    def __init__(self) -> None:
        self._extractors: dict[str, FileExtractor] = {}

    def register(self, extractor: FileExtractor) -> None:
        """Register one extractor by its extractor type."""
        extractor_type = extractor.extractor_type

        if not extractor_type:
            raise ValueError("extractor_type must not be empty")

        if extractor_type in self._extractors:
            raise ValueError(
                f"extractor already registered: {extractor_type}"
            )

        self._extractors[extractor_type] = extractor

    def get(self, extractor_type: str) -> FileExtractor | None:
        """Return the registered extractor, if available."""
        return self._extractors.get(extractor_type)
