from dataclasses import dataclass

import pytest

from personal_ai.file_intelligence.extractors.registry import (
    ExtractedContent,
    ExtractorRegistry,
)


@dataclass(frozen=True)
class FakeExtractor:
    extractor_type: str = "text"

    def extract(self, source_path: str) -> ExtractedContent:
        return ExtractedContent(
            source_path=source_path,
            text="example",
            content_hash="hash",
            extraction_format="text/plain",
            extraction_version="1",
        )


def test_registry_registers_and_resolves_extractor() -> None:
    registry = ExtractorRegistry()
    extractor = FakeExtractor()

    registry.register(extractor)

    assert registry.get("text") is extractor


def test_registry_returns_none_for_unknown_extractor() -> None:
    registry = ExtractorRegistry()

    assert registry.get("pdf") is None


def test_registry_rejects_duplicate_extractor_type() -> None:
    registry = ExtractorRegistry()

    registry.register(FakeExtractor())

    with pytest.raises(ValueError, match="already registered"):
        registry.register(FakeExtractor())


def test_registry_rejects_empty_extractor_type() -> None:
    registry = ExtractorRegistry()

    with pytest.raises(ValueError, match="must not be empty"):
        registry.register(FakeExtractor(extractor_type=""))


def test_extractor_contract_returns_structured_content() -> None:
    extractor = FakeExtractor()

    result = extractor.extract("example.txt")

    assert result.source_path == "example.txt"
    assert result.text == "example"
    assert result.content_hash == "hash"
    assert result.extraction_format == "text/plain"
    assert result.extraction_version == "1"
