
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
