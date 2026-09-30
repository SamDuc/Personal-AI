"""File intelligence orchestration boundary."""

from dataclasses import dataclass
from pathlib import Path

from personal_ai.file_intelligence.capability import (
    FileCapability,
    resolve_file_capability,
)
from personal_ai.file_intelligence.extractors.registry import (
    ExtractedContent,
    ExtractorRegistry,
)
from personal_ai.file_intelligence.normalization import (
    NormalizedContent,
    normalize_extracted_content,
)


@dataclass(frozen=True)
class FileIntelligenceResult:
    """Result produced by the orchestration boundary."""

    source_path: str
    capability: FileCapability
    extracted: ExtractedContent
    normalized: NormalizedContent


class FileIntelligenceOrchestrator:
    """Compose existing file-intelligence boundaries."""

    def __init__(self, extractor_registry: ExtractorRegistry) -> None:
        self._extractor_registry = extractor_registry

    def process(
        self,
        *,
        source_path: str | Path,
        mime_type: str | None,
        extension: str | None,
    ) -> FileIntelligenceResult:
        path = Path(source_path).expanduser().resolve()

        capability = resolve_file_capability(
            mime_type=mime_type,
            extension=extension,
        )

        if not capability.extraction_supported:
            raise ValueError(
                f"Unsupported file capability: {path}"
            )

        extractor_type = capability.extractor_type
        if extractor_type is None:
            raise ValueError(
                f"Supported capability has no extractor type: {path}"
            )

        extractor = self._extractor_registry.get(extractor_type)
        if extractor is None:
            raise ValueError(
                f"No extractor registered for type: {extractor_type}"
            )

        extracted = extractor.extract(str(path))

        normalized = normalize_extracted_content(
            source_path=extracted.source_path,
            text=extracted.text,
            content_hash=extracted.content_hash,
            extraction_format=extracted.extraction_format,
            extraction_version=extracted.extraction_version,
        )

        return FileIntelligenceResult(
            source_path=str(path),
            capability=capability,
            extracted=extracted,
            normalized=normalized,
        )
