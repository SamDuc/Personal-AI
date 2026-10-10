from dataclasses import dataclass
from pathlib import Path

import pytest

from personal_ai.file_intelligence.authorization import AuthorizationGate
from personal_ai.file_intelligence.extractors.registry import (
    ExtractedContent,
    ExtractorRegistry,
)
from personal_ai.file_intelligence.orchestration import (
    FileIntelligenceOrchestrator,
)
from personal_ai.filesystem.scope import FilesystemAccessScope
from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.permissions.policy import PermissionPolicy


@dataclass
class FakeTextExtractor:
    extractor_type: str = "text"
    called: bool = False

    def extract(self, source_path: str) -> ExtractedContent:
        self.called = True
        return ExtractedContent(
            source_path=source_path,
            text="hello personal ai",
            content_hash="abc123",
            extraction_format="text",
            extraction_version="1",
        )


def make_gate(
    root: Path,
    *,
    read: bool = True,
    confirmation_required: list[str] | None = None,
) -> AuthorizationGate:
    policy = PermissionPolicy(
        {
            "defaults": {
                "local_filesystem": {
                    "read": read,
                    "write": False,
                },
            },
            "confirmation_required": confirmation_required or [],
        }
    )

    return AuthorizationGate(
        filesystem_scope=FilesystemAccessScope([root]),
        permission_evaluator=PermissionEvaluator(policy),
    )


def make_orchestrator(
    root: Path,
    *,
    read: bool = True,
    confirmation_required: list[str] | None = None,
) -> tuple[FileIntelligenceOrchestrator, FakeTextExtractor]:
    extractor = FakeTextExtractor()

    registry = ExtractorRegistry()
    registry.register(extractor)

    orchestrator = FileIntelligenceOrchestrator(
        registry,
        make_gate(
            root,
            read=read,
            confirmation_required=confirmation_required,
        ),
    )

    return orchestrator, extractor


def test_orchestrator_resolves_capability_and_extractor(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    orchestrator, extractor = make_orchestrator(tmp_path)

    result = orchestrator.process(
        source_path=path,
        mime_type="text/plain",
        extension=".txt",
    )

    assert result.capability.extraction_supported is True
    assert result.capability.extractor_type == "text"
    assert result.extracted.text == "hello personal ai"
    assert result.normalized.text == "hello personal ai"
    assert result.normalized.content_type == "text"
    assert extractor.called is True


def test_orchestrator_stops_before_extraction_for_unsupported_file(
    tmp_path: Path,
) -> None:
    class FailingExtractor:
        extractor_type = "text"

        def extract(self, source_path: str) -> ExtractedContent:
            raise AssertionError("extractor must not be called")

    registry = ExtractorRegistry()
    registry.register(FailingExtractor())

    orchestrator = FileIntelligenceOrchestrator(
        registry,
        make_gate(tmp_path),
    )

    path = tmp_path / "document.pdf"
    path.write_bytes(b"%PDF")

    with pytest.raises(ValueError, match="Unsupported file capability"):
        orchestrator.process(
            source_path=path,
            mime_type="application/pdf",
            extension=".pdf",
        )


def test_orchestrator_stops_before_extraction_when_scope_is_denied(
    tmp_path: Path,
) -> None:
    authorized = tmp_path / "authorized"
    outside = tmp_path / "outside"
    authorized.mkdir()
    outside.mkdir()

    path = outside / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    extractor = FakeTextExtractor()
    registry = ExtractorRegistry()
    registry.register(extractor)

    orchestrator = FileIntelligenceOrchestrator(
        registry,
        make_gate(authorized),
    )

    with pytest.raises(
        PermissionError,
        match="filesystem_scope_denied",
    ):
        orchestrator.process(
            source_path=path,
            mime_type="text/plain",
            extension=".txt",
        )

    assert extractor.called is False


def test_orchestrator_stops_before_extraction_when_permission_is_denied(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    orchestrator, extractor = make_orchestrator(
        tmp_path,
        read=False,
    )

    with pytest.raises(
        PermissionError,
        match="permission_denied",
    ):
        orchestrator.process(
            source_path=path,
            mime_type="text/plain",
            extension=".txt",
        )

    assert extractor.called is False


def test_orchestrator_stops_before_extraction_when_confirmation_is_required(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    orchestrator, extractor = make_orchestrator(
        tmp_path,
        confirmation_required=["read"],
    )

    with pytest.raises(
        PermissionError,
        match="permission_confirmation_required",
    ):
        orchestrator.process(
            source_path=path,
            mime_type="text/plain",
            extension=".txt",
        )

    assert extractor.called is False


def test_orchestrator_fails_when_extractor_is_missing(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    orchestrator = FileIntelligenceOrchestrator(
        ExtractorRegistry(),
        make_gate(tmp_path),
    )

    with pytest.raises(
        ValueError,
        match="No extractor registered for type: text",
    ):
        orchestrator.process(
            source_path=path,
            mime_type="text/plain",
            extension=".txt",
        )


def test_orchestrator_does_not_perform_indexing(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    orchestrator, _ = make_orchestrator(tmp_path)

    result = orchestrator.process(
        source_path=path,
        mime_type="text/plain",
        extension=".txt",
    )

    assert result.normalized.content_type == "text"
    assert not hasattr(result, "indexed")
