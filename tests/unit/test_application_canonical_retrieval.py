
from personal_ai.application.canonical_retriever import (
    LocalCanonicalRetrieval,
)
from personal_ai.retrieval.local import RetrievalRequest


def test_canonical_retrieval_rejects_empty_query(tmp_path):
    retrieval = LocalCanonicalRetrieval(
        filesystem_scope=__import__(
            "personal_ai.filesystem.scope",
            fromlist=["FilesystemAccessScope"],
        ).FilesystemAccessScope(
            authorized_roots=(tmp_path,),
        ),
        source_config=__import__(
            "personal_ai.sources.config",
            fromlist=["SourceConfig"],
        ).SourceConfig(
            {"sources": {"local_filesystem": {"enabled": True}}},
        ),
        permission_evaluator=__import__(
            "personal_ai.permissions.evaluator",
            fromlist=["PermissionEvaluator"],
        ).PermissionEvaluator(
            {
                "defaults": {
                    "local_filesystem": {"read": True},
                },
                "confirmation_required": [],
            }
        ),
    )

    try:
        retrieval.retrieve(RetrievalRequest(query="   "))
    except ValueError as exc:
        assert "must not be empty" in str(exc)
    else:
        raise AssertionError("Expected empty retrieval query to fail")


def test_retrieval_uses_refreshed_catalog_without_discovery(tmp_path, monkeypatch):
    import personal_ai.application.canonical_retriever as retriever_module
    from personal_ai.filesystem.scope import FilesystemAccessScope
    from personal_ai.permissions.evaluator import PermissionEvaluator
    from personal_ai.permissions.policy import PermissionPolicy
    from personal_ai.sources.config import SourceConfig

    source_file = tmp_path / "existing.txt"
    source_file.write_text("retrieval catalog sentinel", encoding="utf-8")

    retrieval = LocalCanonicalRetrieval(
        filesystem_scope=FilesystemAccessScope([tmp_path]),
        source_config=SourceConfig(
            {"sources": {"local_filesystem": {"enabled": True}}}
        ),
        permission_evaluator=PermissionEvaluator(
            PermissionPolicy(
                {
                    "defaults": {"local_filesystem": {"read": True}},
                    "confirmation_required": [],
                }
            )
        ),
    )

    assert retrieval.refresh() == 1

    def unexpected_discovery(*args, **kwargs):
        raise AssertionError("Retrieval must not discover files")

    monkeypatch.setattr(
        retriever_module,
        "discover_enabled_local_files",
        unexpected_discovery,
    )

    results = retrieval.retrieve(
        RetrievalRequest(query="retrieval catalog sentinel")
    )
    assert len(results) == 1
    assert results[0].item.source_id == str(source_file)
def test_refresh_rolls_back_earlier_files_when_batch_fails(
    tmp_path, monkeypatch
):
    import pytest

    from personal_ai.application.canonical_retriever import (
        LocalCanonicalRetrieval,
    )
    from personal_ai.filesystem.scope import FilesystemAccessScope
    from personal_ai.permissions.evaluator import PermissionEvaluator
    from personal_ai.permissions.policy import PermissionPolicy
    from personal_ai.sources.config import SourceConfig

    source_files = [
        tmp_path / "a.txt",
        tmp_path / "b.txt",
    ]
    for path in source_files:
        path.write_text("original content", encoding="utf-8")

    retrieval = LocalCanonicalRetrieval(
        filesystem_scope=FilesystemAccessScope([tmp_path]),
        source_config=SourceConfig(
            {"sources": {"local_filesystem": {"enabled": True}}}
        ),
        permission_evaluator=PermissionEvaluator(
            PermissionPolicy(
                {
                    "defaults": {"local_filesystem": {"read": True}},
                    "confirmation_required": [],
                }
            )
        ),
    )

    assert retrieval.refresh() == 2

    content_index = retrieval.content_index
    assert content_index is not None

    previous_states = {
        str(path): content_index.get(str(path))
        for path in source_files
    }
    assert all(state is not None for state in previous_states.values())

    for path in source_files:
        path.write_text("updated content", encoding="utf-8")

    original_refresh = retrieval._refresh_service.refresh
    calls = 0
    first_source = None

    def fail_on_second_refresh(item, **kwargs):
        nonlocal calls, first_source
        calls += 1

        if calls == 1:
            first_source = item.source_id
            return original_refresh(item, **kwargs)

        raise RuntimeError("simulated second-file refresh failure")

    monkeypatch.setattr(
        retrieval._refresh_service,
        "refresh",
        fail_on_second_refresh,
    )

    with pytest.raises(
        RuntimeError,
        match="simulated second-file refresh failure",
    ):
        retrieval.refresh()

    assert first_source is not None
    assert content_index.get(first_source) == previous_states[first_source]
    assert retrieval._catalog
    assert {
        source_path: content_index.get(source_path)
        for source_path in previous_states
    } == previous_states
def test_catalog_is_cleared_when_batch_rollback_fails(
    tmp_path, monkeypatch
):
    import pytest

    from personal_ai.application.canonical_retriever import (
        LocalCanonicalRetrieval,
    )
    from personal_ai.filesystem.scope import FilesystemAccessScope
    from personal_ai.permissions.evaluator import PermissionEvaluator
    from personal_ai.permissions.policy import PermissionPolicy
    from personal_ai.retrieval.local import RetrievalRequest
    from personal_ai.sources.config import SourceConfig

    source_file = tmp_path / "rollback-failure.txt"
    source_file.write_text("original content", encoding="utf-8")

    retrieval = LocalCanonicalRetrieval(
        filesystem_scope=FilesystemAccessScope([tmp_path]),
        source_config=SourceConfig(
            {"sources": {"local_filesystem": {"enabled": True}}}
        ),
        permission_evaluator=PermissionEvaluator(
            PermissionPolicy(
                {
                    "defaults": {"local_filesystem": {"read": True}},
                    "confirmation_required": [],
                }
            )
        ),
    )

    assert retrieval.refresh() == 1
    assert retrieval._catalog

    def fail_refresh(*args, **kwargs):
        raise RuntimeError("simulated refresh failure")

    def fail_rollback(*args, **kwargs):
        raise OSError("simulated rollback failure")

    monkeypatch.setattr(
        retrieval._refresh_service, "refresh", fail_refresh
    )
    monkeypatch.setattr(
        retrieval.content_index, "restore_source_state", fail_rollback
    )

    with pytest.raises(ExceptionGroup):
        retrieval.refresh()

    assert retrieval._catalog == {}
    assert retrieval.retrieve(
        RetrievalRequest(query="original content")
    ) == []

def test_refresh_removes_deleted_file_from_retrieval_catalog(
    tmp_path, monkeypatch
):
    from personal_ai.application.canonical_retriever import (
        LocalCanonicalRetrieval,
    )
    from personal_ai.filesystem.scope import FilesystemAccessScope
    from personal_ai.permissions.evaluator import PermissionEvaluator
    from personal_ai.permissions.policy import PermissionPolicy
    from personal_ai.retrieval.local import RetrievalRequest
    from personal_ai.sources.config import SourceConfig

    source_file = tmp_path / "deleted-after-refresh.txt"
    source_file.write_text("deleted file sentinel", encoding="utf-8")

    retrieval = LocalCanonicalRetrieval(
        filesystem_scope=FilesystemAccessScope([tmp_path]),
        source_config=SourceConfig(
            {"sources": {"local_filesystem": {"enabled": True}}}
        ),
        permission_evaluator=PermissionEvaluator(
            PermissionPolicy(
                {
                    "defaults": {"local_filesystem": {"read": True}},
                    "confirmation_required": [],
                }
            )
        ),
    )

    assert retrieval.refresh() == 1
    assert retrieval._catalog

    source_file.unlink()

    assert retrieval.refresh() == 0
    assert retrieval._catalog == {}
    assert retrieval.retrieve(
        RetrievalRequest(query="deleted file sentinel")
    ) == []
