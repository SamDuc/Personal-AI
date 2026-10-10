"""File intelligence orchestration boundary."""

from dataclasses import dataclass
from pathlib import Path

from personal_ai.file_intelligence.authorization import AuthorizationGate
from personal_ai.file_intelligence.capability import (
    FileCapability,
    resolve_file_capability,
)
from personal_ai.file_intelligence.consistency import (
    SourceSnapshot,
    snapshot_local_file,
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
    source_snapshot: SourceSnapshot


class FileIntelligenceOrchestrator:
    """Compose capability, authorization, extraction, and normalization."""

    def __init__(
        self,
        extractor_registry: ExtractorRegistry,
        authorization_gate: AuthorizationGate,
    ) -> None:
        self._extractor_registry = extractor_registry
        self._authorization_gate = authorization_gate

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

        decision = self._authorization_gate.evaluate(
            source_path=path,
            capability=capability,
            resource_category="local_filesystem",
            operation="read",
        )

        if not decision.allowed:
            raise PermissionError(
                f"File authorization denied: {decision.reason}: {path}"
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

        # Snapshot only after authorization and before extraction.
        source_snapshot_before = snapshot_local_file(path)
        extracted = extractor.extract(str(path))
        source_snapshot_after = snapshot_local_file(path)

        if source_snapshot_before != source_snapshot_after:
            raise RuntimeError(
                f"Source file changed during extraction: {path}"
            )

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
            source_snapshot=source_snapshot_after,
        )
