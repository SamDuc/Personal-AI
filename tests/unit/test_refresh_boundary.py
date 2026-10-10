
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path

import pytest

import personal_ai.file_intelligence.refresh as refresh_module
from personal_ai.core.models import DataItem
from personal_ai.file_intelligence.authorization import AuthorizationGate
from personal_ai.file_intelligence.consistency import (
    snapshot_local_file,
)
from personal_ai.file_intelligence.extractors.registry import (
    ExtractedContent,
    ExtractorRegistry,
)
from personal_ai.file_intelligence.index import ContentIndex
from personal_ai.file_intelligence.orchestration import (
    FileIntelligenceOrchestrator,
)
from personal_ai.file_intelligence.refresh import (
    LocalFileRefresh,
)
from personal_ai.filesystem.scope import FilesystemAccessScope
from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.permissions.policy import PermissionPolicy


class FakeTextExtractor:
    extractor_type = "text"

    def __init__(self, mutate_path: Path | None = None) -> None:
        self.called = False
        self.mutate_path = mutate_path

    def extract(self, source_path: str) -> ExtractedContent:
        self.called = True
        if self.mutate_path is not None:
            self.mutate_path.write_text(
                "changed during extraction",
                encoding="utf-8",
            )
        return ExtractedContent(
            source_path=source_path,
            text="hello personal ai",
            content_hash="abc123",
            extraction_format="text",
            extraction_version="1",
        )


def make_item(path: Path) -> DataItem:
    resolved = str(path.resolve())
    return DataItem(
        id=f"local:{resolved}",
        source="local_filesystem",
        source_id=resolved,
        uri=resolved,
        item_type="file",
        mime_type="text/plain",
        extension=".txt",
        name=path.name,
        size=path.stat().st_size,
        created_at=datetime.now(UTC),
        modified_at=datetime.fromtimestamp(
            path.stat().st_mtime,
            tz=UTC,
        ),
    )


def make_refresh(
    root: Path,
    *,
    read: bool = True,
    mutate_path: Path | None = None,
) -> tuple[LocalFileRefresh, FakeTextExtractor, ContentIndex]:
    extractor = FakeTextExtractor(mutate_path=mutate_path)

    registry = ExtractorRegistry()
    registry.register(extractor)

    policy = PermissionPolicy(
        {
            "defaults": {
                "local_filesystem": {
                    "read": read,
                    "write": False,
                },
            },
            "confirmation_required": [],
        }
    )

    gate = AuthorizationGate(
        filesystem_scope=FilesystemAccessScope([root]),
        permission_evaluator=PermissionEvaluator(policy),
    )

    orchestrator = FileIntelligenceOrchestrator(
        registry,
        gate,
    )
    content_index = ContentIndex()

    refresh = LocalFileRefresh(
        orchestrator=orchestrator,
        content_index=content_index,
    )

    return refresh, extractor, content_index


def test_refresh_rejects_source_changed_during_extraction(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    item = make_item(path)
    refresh, extractor, index = make_refresh(
        tmp_path,
        mutate_path=path,
    )

    with pytest.raises(RuntimeError, match="changed during extraction"):
        refresh.refresh(
            item,
            mime_type="text/plain",
            extension=".txt",
        )

    assert extractor.called is True
    assert index.get(str(path.resolve())) is None
    assert item.content_available is False

def test_refresh_rejects_source_changed_before_indexing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    item = make_item(path)
    refresh, extractor, index = make_refresh(tmp_path)

    original_snapshot = refresh_module.snapshot_local_file
    original_index = index.index
    index_calls = 0

    def track_index(content, *, content_ref, indexed_at):
        nonlocal index_calls
        index_calls += 1
        return original_index(
            content,
            content_ref=content_ref,
            indexed_at=indexed_at,
        )

    def mutate_before_snapshot(source_path):
        path.write_text(
            "changed before indexing",
            encoding="utf-8",
        )
        return original_snapshot(source_path)

    monkeypatch.setattr(index, "index", track_index)
    monkeypatch.setattr(
        refresh_module,
        "snapshot_local_file",
        mutate_before_snapshot,
    )

    with pytest.raises(
        RuntimeError,
        match="changed after extraction and before indexing",
    ):
        refresh.refresh(
            item,
            mime_type="text/plain",
            extension=".txt",
        )

    assert extractor.called is True
    assert index_calls == 0
    assert index.get(str(path.resolve())) is None
    assert item.content_available is False
    assert item.content_ref is None
    assert item.content_hash is None


def test_refresh_indexes_normalized_content(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    item = make_item(path)
    refresh, extractor, index = make_refresh(tmp_path)

    result = refresh.refresh(
        item,
        mime_type="text/plain",
        extension=".txt",
    )

    indexed = index.get(str(path.resolve()))

    assert extractor.called is True
    assert result.item is item
    assert result.item.content_available is True
    assert result.item.searchable is True
    assert result.item.content_hash == "abc123"
    assert result.item.content_ref == "index://content/abc123"
    assert result.item.sync_status == "indexed"
    assert indexed is not None
    assert indexed.content_hash == "abc123"
    assert indexed.searchable is True
    assert indexed.sync_status == "indexed"


def test_refresh_associates_current_source_snapshot(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    item = make_item(path)
    refresh, _, _ = make_refresh(tmp_path)

    result = refresh.refresh(
        item,
        mime_type="text/plain",
        extension=".txt",
    )

    expected = snapshot_local_file(path)

    assert result.source_snapshot.source == "local_filesystem"
    assert result.source_snapshot.source_id == str(path.resolve())
    assert result.item.source_modified_at == expected.modified_at


def test_refresh_records_index_and_source_timestamps_separately(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    item = make_item(path)
    refresh, _, index = make_refresh(tmp_path)

    result = refresh.refresh(
        item,
        mime_type="text/plain",
        extension=".txt",
    )

    indexed = index.get(str(path.resolve()))

    assert indexed is not None
    assert result.item.indexed_at == indexed.indexed_at
    assert result.item.source_modified_at == result.source_snapshot.modified_at

    indexed_at = datetime.fromisoformat(result.item.indexed_at)
    assert indexed_at.tzinfo is not None
    assert indexed_at.utcoffset() is not None

def test_refresh_rejects_non_local_source(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    item = make_item(path)
    item.source = "remote"

    refresh, _, _ = make_refresh(tmp_path)

    with pytest.raises(ValueError, match="local_filesystem"):
        refresh.refresh(
            item,
            mime_type="text/plain",
            extension=".txt",
        )


def test_refresh_propagates_authorization_failure(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    item = make_item(path)
    refresh, extractor, _ = make_refresh(
        tmp_path,
        read=False,
    )

    with pytest.raises(
        PermissionError,
        match="permission_denied",
    ):
        refresh.refresh(
            item,
            mime_type="text/plain",
            extension=".txt",
        )

    assert extractor.called is False


def test_refresh_propagates_unsupported_capability(
    tmp_path: Path,
) -> None:
    path = tmp_path / "document.pdf"
    path.write_bytes(b"%PDF")

    item = make_item(path)
    refresh, extractor, _ = make_refresh(tmp_path)

    with pytest.raises(
        ValueError,
        match="Unsupported file capability",
    ):
        refresh.refresh(
            item,
            mime_type="application/pdf",
            extension=".pdf",
        )

    assert extractor.called is False


def test_refresh_propagates_missing_source(
    tmp_path: Path,
) -> None:
    path = tmp_path / "missing.txt"

    item = DataItem(
        id=f"local:{path.resolve()}",
        source="local_filesystem",
        source_id=str(path.resolve()),
        uri=str(path.resolve()),
        item_type="file",
        mime_type="text/plain",
        extension=".txt",
        name=path.name,
        size=0,
        created_at=datetime.now(UTC),
        modified_at=datetime.now(UTC),
    )

    refresh, _, _ = make_refresh(tmp_path)

    with pytest.raises(FileNotFoundError):
        refresh.refresh(
            item,
            mime_type="text/plain",
            extension=".txt",
        )


def test_refresh_does_not_modify_source_content(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    original = "hello"
    path.write_text(original, encoding="utf-8")

    item = make_item(path)
    refresh, _, _ = make_refresh(tmp_path)

    refresh.refresh(
        item,
        mime_type="text/plain",
        extension=".txt",
    )

    assert path.read_text(encoding="utf-8") == original


def test_refresh_requires_explicit_invocation(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    item = make_item(path)
    refresh, extractor, index = make_refresh(tmp_path)

    assert extractor.called is False
    assert index.get(str(path.resolve())) is None
    assert item.content_available is False

    refresh.refresh(
        item,
        mime_type="text/plain",
        extension=".txt",
    )

    assert extractor.called is True
    assert index.get(str(path.resolve())) is not None


def test_refresh_does_not_use_legacy_orchestration_path(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    item = make_item(path)
    refresh, _, index = make_refresh(tmp_path)

    result = refresh.refresh(
        item,
        mime_type="text/plain",
        extension=".txt",
    )

    indexed = index.get(str(path.resolve()))

    assert result.item.content_ref == "index://content/abc123"
    assert indexed is not None
    assert indexed.content_ref == "index://content/abc123"

def test_refresh_rejects_source_changed_during_indexing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    item = make_item(path)
    refresh, extractor, index = make_refresh(tmp_path)

    original_index = index.index

    def mutate_during_index(content, *, content_ref, indexed_at):
        indexed = original_index(
            content,
            content_ref=content_ref,
            indexed_at=indexed_at,
        )
        path.write_text(
            "changed during indexing",
            encoding="utf-8",
        )
        return indexed

    monkeypatch.setattr(index, "index", mutate_during_index)

    with pytest.raises(RuntimeError, match="changed during indexing"):
        refresh.refresh(
            item,
            mime_type="text/plain",
            extension=".txt",
        )

    assert extractor.called is True
    assert index.get(str(path.resolve())) is None
    assert item.content_available is False

def test_refresh_restores_previous_index_when_source_changes_during_indexing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    item = make_item(path)
    refresh, extractor, index = make_refresh(tmp_path)

    # Establish a valid index that must survive a failed subsequent refresh.
    refresh.refresh(
        item,
        mime_type="text/plain",
        extension=".txt",
    )
    source_path = str(path.resolve())
    previous_index = index.get(source_path)
    assert previous_index is not None
    previous_content = index.get_content(
        previous_index.content_ref,
        source_path=source_path,
        content_hash=previous_index.content_hash,
    )
    assert previous_content is not None
    assert previous_content.strip()

    previous_item_state = (
        item.content_available,
        item.content_ref,
        item.content_hash,
        item.searchable,
        item.indexed_at,
        item.source_modified_at,
        item.sync_status,
    )

    # Change the source before the second extraction/index operation.
    path.write_text("new content", encoding="utf-8")
    original_index = index.index

    def mutate_during_index(content, *, content_ref, indexed_at):
        indexed = original_index(
            content,
            content_ref=content_ref,
            indexed_at=indexed_at,
        )
        path.write_text(
            "changed during indexing",
            encoding="utf-8",
        )
        return indexed

    monkeypatch.setattr(index, "index", mutate_during_index)

    with pytest.raises(RuntimeError, match="changed during indexing"):
        refresh.refresh(
            item,
            mime_type="text/plain",
            extension=".txt",
        )

    assert extractor.called is True
    assert index.get(source_path) == previous_index
    assert index.get_content(
        previous_index.content_ref,
        source_path=source_path,
        content_hash=previous_index.content_hash,
    ) == previous_content

    assert (
        item.content_available,
        item.content_ref,
        item.content_hash,
        item.searchable,
        item.indexed_at,
        item.source_modified_at,
        item.sync_status,
    ) == previous_item_state


def test_concurrent_refreshes_serialize_per_source(
    tmp_path: Path,
) -> None:
    path = tmp_path / "concurrent.txt"
    path.write_text("hello", encoding="utf-8")
    item_one = make_item(path)
    item_two = make_item(path)
    refresh_one, _, content_index = make_refresh(tmp_path)
    refresh_two = LocalFileRefresh(
        orchestrator=refresh_one._orchestrator,
        content_index=content_index,
    )

    original_process = refresh_one._orchestrator.process
    first_entered = threading.Event()
    release_first = threading.Event()
    second_entered_process = threading.Event()
    second_started = threading.Event()
    counter_lock = threading.Lock()
    active = 0
    max_active = 0
    call_count = 0

    def controlled_process(**kwargs):
        nonlocal active, max_active, call_count
        with counter_lock:
            call_count += 1
            this_call = call_count
            active += 1
            max_active = max(max_active, active)

        if this_call == 1:
            first_entered.set()
            if not release_first.wait(timeout=5):
                raise TimeoutError("Timed out waiting to release first refresh")
        else:
            second_entered_process.set()

        try:
            return original_process(**kwargs)
        finally:
            with counter_lock:
                active -= 1

    refresh_one._orchestrator.process = controlled_process

    def run_second():
        second_started.set()
        return refresh_two.refresh(
            item_two,
            mime_type="text/plain",
            extension=".txt",
        )

    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            first_future = pool.submit(
                refresh_one.refresh,
                item_one,
                mime_type="text/plain",
                extension=".txt",
            )
            assert first_entered.wait(timeout=2)

            second_future = pool.submit(run_second)
            assert second_started.wait(timeout=2)

            # The second extraction must not enter while the first refresh
            # holds the per-source lock.
            assert not second_entered_process.wait(timeout=0.2)

            release_first.set()
            first_future.result(timeout=5)
            second_future.result(timeout=5)

        assert max_active == 1
        assert call_count == 2
        indexed = content_index.get(str(path.resolve()))
        assert indexed is not None
        assert content_index.get_content(
            indexed.content_ref,
            source_path=str(path.resolve()),
            content_hash=indexed.content_hash,
        )
    finally:
        release_first.set()
        refresh_one._orchestrator.process = original_process

def test_refresh_groups_errors_when_index_rollback_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")
    item = make_item(path)
    refresh, _, index = make_refresh(tmp_path)

    def fail_index(content, *, content_ref, indexed_at):
        raise RuntimeError("index failed")

    def fail_restore(state):
        raise LookupError("rollback failed")

    monkeypatch.setattr(index, "index", fail_index)
    monkeypatch.setattr(index, "restore_source_state", fail_restore)

    with pytest.raises(
        ExceptionGroup,
        match="Refresh failed and index rollback also failed",
    ) as exc_info:
        refresh.refresh(
            item,
            mime_type="text/plain",
            extension=".txt",
        )

    errors = exc_info.value.exceptions
    assert len(errors) == 2
    assert isinstance(errors[0], RuntimeError)
    assert str(errors[0]) == "index failed"
    assert isinstance(errors[1], LookupError)
    assert str(errors[1]) == "rollback failed"
