from dataclasses import dataclass

import pytest

from personal_ai.file_intelligence.extractors.registry import (
    ExtractedContent,
    ExtractorRegistry,
)
from personal_ai.file_intelligence.orchestration import (
    FileIntelligenceOrchestrator,
)


@dataclass
class FakeTextExtractor:
    extractor_type: str = "text"

    def extract(self, source_path: str) -> ExtractedContent:
        return ExtractedContent(
            source_path=source_path,
            text="hello personal ai",
            content_hash="abc123",
            extraction_format="text",
            extraction_version="1",
        )


def make_orchestrator() -> FileIntelligenceOrchestrator:
    registry = ExtractorRegistry()
    registry.register(FakeTextExtractor())
    return FileIntelligenceOrchestrator(registry)


def test_orchestrator_resolves_capability_and_extractor() -> None:
    orchestrator = make_orchestrator()

    result = orchestrator.process(
        source_path="notes.txt",
        mime_type="text/plain",
        extension=".txt",
    )

    assert result.capability.extraction_supported is True
    assert result.capability.extractor_type == "text"
    assert result.extracted.text == "hello personal ai"
    assert result.normalized.text == "hello personal ai"
    assert result.normalized.content_type == "text"


def test_orchestrator_stops_before_extraction_for_unsupported_file() -> None:
    class FailingExtractor:
        extractor_type = "text"

        def extract(self, source_path: str) -> ExtractedContent:
            raise AssertionError("extractor must not be called")

    registry = ExtractorRegistry()
    registry.register(FailingExtractor())

    orchestrator = FileIntelligenceOrchestrator(registry)

    with pytest.raises(ValueError, match="Unsupported file capability"):
        orchestrator.process(
            source_path="document.pdf",
            mime_type="application/pdf",
            extension=".pdf",
        )


def test_orchestrator_fails_when_extractor_is_missing() -> None:
    orchestrator = FileIntelligenceOrchestrator(
        ExtractorRegistry()
    )

    with pytest.raises(
        ValueError,
        match="No extractor registered for type: text",
    ):
        orchestrator.process(
            source_path="notes.txt",
            mime_type="text/plain",
            extension=".txt",
        )


def test_orchestrator_does_not_perform_indexing() -> None:
    orchestrator = make_orchestrator()

    result = orchestrator.process(
        source_path="notes.txt",
        mime_type="text/plain",
        extension=".txt",
    )

    assert result.normalized.content_type == "text"
    assert not hasattr(result, "indexed")
