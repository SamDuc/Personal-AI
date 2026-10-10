from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event

import pytest

from personal_ai.application.canonical_retriever import LocalCanonicalRetrieval
from personal_ai.application.file_intelligence import LocalFileApplicationIngestion
from personal_ai.core.models import AccessPolicy, DataItem
from personal_ai.file_intelligence.authorization import AuthorizationGate
from personal_ai.file_intelligence.extractors import ExtractedContent, ExtractorRegistry
from personal_ai.file_intelligence.orchestration import FileIntelligenceOrchestrator
from personal_ai.filesystem.scope import FilesystemAccessScope
from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.permissions.policy import PermissionPolicy
from personal_ai.sources.config import SourceConfig


def test_batch_rollback_serializes_concurrent_ingestion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_a = tmp_path / "a.txt"
    source_b = tmp_path / "b.txt"
    source_a.write_text("original A", encoding="utf-8")
    source_b.write_text("original B", encoding="utf-8")

    scope = FilesystemAccessScope([tmp_path])
    permissions = PermissionEvaluator(
        PermissionPolicy(
            {
                "defaults": {"local_filesystem": {"read": True}},
                "confirmation_required": [],
            }
        )
    )
    retrieval = LocalCanonicalRetrieval(
        filesystem_scope=scope,
        source_config=SourceConfig(
            {"sources": {"local_filesystem": {"enabled": True}}}
        ),
        permission_evaluator=permissions,
    )
    assert retrieval.refresh() == 2

    index = retrieval.content_index
    assert index is not None
    source_key = str(source_a.resolve())
    original_state = index.get(source_key)
    assert original_state is not None

    source_a.write_text("batch version A", encoding="utf-8")
    source_b.write_text("batch version B", encoding="utf-8")

    batch_a_refreshed = Event()
    allow_batch_to_continue = Event()
    ingestion_finished = Event()
    writer_started = Event()

    original_refresh = retrieval._refresh_service.refresh
    call_count = 0

    def controlled_refresh(item, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            result = original_refresh(item, **kwargs)
            if item.source_id == source_key:
                batch_a_refreshed.set()
                if not allow_batch_to_continue.wait(timeout=5):
                    raise TimeoutError("Batch continuation timed out")
            return result
        raise RuntimeError("simulated second-file refresh failure")

    monkeypatch.setattr(
        retrieval._refresh_service, "refresh", controlled_refresh
    )

    registry = ExtractorRegistry()

    class TextExtractor:
        extractor_type = "text"

        def extract(self, source_path: str) -> ExtractedContent:
            path = Path(source_path)
            return ExtractedContent(
                source_path=str(path.resolve()),
                text=path.read_text(encoding="utf-8"),
                content_hash="concurrent-ingestion-hash",
                extraction_format="text",
                extraction_version="1",
            )

    registry.register(TextExtractor())
    ingestion = LocalFileApplicationIngestion(
        orchestrator=FileIntelligenceOrchestrator(
            extractor_registry=registry,
            authorization_gate=AuthorizationGate(
                filesystem_scope=scope,
                permission_evaluator=permissions,
            ),
        ),
        content_index=index,
    )

    def concurrent_writer():
        if not batch_a_refreshed.wait(timeout=5):
            raise TimeoutError("Batch did not refresh source A")

        writer_started.set()
        source_a.write_text("concurrent version A", encoding="utf-8")
        item = DataItem(
            id=f"local:{source_key}",
            source="local_filesystem",
            source_id=source_key,
            uri=source_a.resolve().as_uri(),
            item_type="file",
            mime_type="text/plain",
            extension=".txt",
            name=source_a.name,
            size=source_a.stat().st_size,
            access_policy=AccessPolicy(read=True, write=False),
        )
        try:
            ingestion.ingest(item, mime_type="text/plain", extension=".txt")
        finally:
            ingestion_finished.set()

    with ThreadPoolExecutor(max_workers=2) as pool:
        batch_future = pool.submit(retrieval.refresh)
        writer_future = pool.submit(concurrent_writer)
        try:
            assert batch_a_refreshed.wait(timeout=5)
            assert writer_started.wait(timeout=5)
            assert not ingestion_finished.wait(timeout=0.3)
        finally:
            allow_batch_to_continue.set()

        with pytest.raises(
            RuntimeError, match="simulated second-file refresh failure"
        ):
            batch_future.result(timeout=5)
        writer_future.result(timeout=5)

    current_state = index.get(source_key)
    assert current_state is not None
    assert current_state.content_hash == "concurrent-ingestion-hash"
    assert current_state != original_state
