from pathlib import Path

from personal_ai.application.local_retriever import create_local_retriever
from personal_ai.filesystem.scope import FilesystemAccessScope
from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.permissions.policy import PermissionPolicy
from personal_ai.sources.config import SourceConfig


def test_application_retrieval_uses_canonical_file_intelligence(
    tmp_path: Path,
) -> None:
    target = tmp_path / "notes.txt"
    target.write_text(
        "canonical ingestion pipeline validation",
        encoding="utf-8",
    )

    scope = FilesystemAccessScope(authorized_roots=(tmp_path,))
    source_config = SourceConfig(
        {
            "sources": {
                "local_filesystem": {
                    "enabled": True,
                }
            }
        }
    )
    permission_evaluator = PermissionEvaluator(
        PermissionPolicy(
            {
                "defaults": {
                    "local_filesystem": {
                        "read": True,
                    },
                },
                "confirmation_required": [],
            }
        )
    )

    retrieve = create_local_retriever(
        filesystem_scope=scope,
        source_config=source_config,
        permission_evaluator=permission_evaluator,
    )

    results = retrieve("canonical ingestion")

    assert results == ["canonical ingestion pipeline validation"]


def test_application_retrieval_returns_nothing_when_source_disabled(
    tmp_path: Path,
) -> None:
    target = tmp_path / "notes.txt"
    target.write_text("must not be processed", encoding="utf-8")

    scope = FilesystemAccessScope(authorized_roots=(tmp_path,))
    source_config = SourceConfig(
        {
            "sources": {
                "local_filesystem": {
                    "enabled": False,
                }
            }
        }
    )
    permission_evaluator = PermissionEvaluator(
        PermissionPolicy(
            {
                "defaults": {
                    "local_filesystem": {
                        "read": True,
                    },
                },
                "confirmation_required": [],
            }
        )
    )

    retrieve = create_local_retriever(
        filesystem_scope=scope,
        source_config=source_config,
        permission_evaluator=permission_evaluator,
    )

    assert retrieve("must not") == []


def test_application_retrieval_returns_nothing_when_permission_denied(
    tmp_path: Path,
) -> None:
    target = tmp_path / "notes.txt"
    target.write_text("must not be processed", encoding="utf-8")

    scope = FilesystemAccessScope(authorized_roots=(tmp_path,))
    source_config = SourceConfig(
        {
            "sources": {
                "local_filesystem": {
                    "enabled": True,
                }
            }
        }
    )
    permission_evaluator = PermissionEvaluator(
        PermissionPolicy(
            {
                "defaults": {
                    "local_filesystem": {
                        "read": False,
                    },
                },
                "confirmation_required": [],
            }
        )
    )

    retrieve = create_local_retriever(
        filesystem_scope=scope,
        source_config=source_config,
        permission_evaluator=permission_evaluator,
    )

    assert retrieve("must not") == []