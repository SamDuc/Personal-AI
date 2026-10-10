from pathlib import Path

from personal_ai.core.models import AccessPolicy, DataItem
from personal_ai.file_intelligence.index import ContentIndex
from personal_ai.file_intelligence.normalization import (
    normalize_extracted_content,
)
from personal_ai.filesystem.scope import FilesystemAccessScope
from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.permissions.policy import PermissionPolicy
from personal_ai.sources.config import SourceConfig


def make_access(tmp_path: Path, *, read: bool = True, enabled: bool = True):
    from personal_ai.application.canonical_content_access import (
        LocalCanonicalContentAccess,
    )

    return LocalCanonicalContentAccess(
        filesystem_scope=FilesystemAccessScope([tmp_path]),
        source_config=SourceConfig(
            {"sources": {"local_filesystem": {"enabled": enabled}}}
        ),
        permission_evaluator=PermissionEvaluator(
            PermissionPolicy(
                {
                    "defaults": {"local_filesystem": {"read": read}},
                    "confirmation_required": [],
                }
            )
        ),
        content_index=ContentIndex(),
    )


def make_item(path: Path, **overrides) -> DataItem:
    values = {
        "id": "item-1",
        "source": "local_filesystem",
        "source_id": str(path),
        "uri": path.as_uri(),
        "item_type": "file",
        "mime_type": "text/plain",
        "extension": ".txt",
        "name": path.name,
        "content_available": True,
        "content_ref": "index://content/item-1",
        "content_hash": "hash-item-1",
        "searchable": True,
        "sync_status": "indexed",
        "access_policy": AccessPolicy(read=True, write=False),
    }
    values.update(overrides)
    return DataItem(**values)


def make_index(path: Path) -> ContentIndex:
    index = ContentIndex()
    normalized = normalize_extracted_content(
        source_path=str(path),
        text="authorized document content",
        content_hash="hash-item-1",
        extraction_format="text/plain",
        extraction_version="1",
    )
    index.index(
        normalized,
        content_ref="index://content/item-1",
        indexed_at="2026-10-01T00:00:00+00:00",
    )
    return index


def test_content_access_reads_indexed_content_within_authorized_scope(tmp_path):
    from personal_ai.application.canonical_content_access import (
        LocalCanonicalContentAccess,
    )

    path = tmp_path / "notes.txt"
    index = make_index(path)
    access = LocalCanonicalContentAccess(
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
        content_index=index,
    )

    assert access.read(make_item(path)) == "authorized document content"


def test_content_access_returns_none_when_content_is_unavailable(tmp_path):
    access = make_access(tmp_path)
    item = make_item(
        tmp_path / "notes.txt",
        content_available=False,
    )

    assert access.read(item) is None


def test_content_access_returns_none_when_item_read_policy_denies(tmp_path):
    access = make_access(tmp_path)
    item = make_item(
        tmp_path / "notes.txt",
        access_policy=AccessPolicy(read=False, write=False),
    )

    assert access.read(item) is None


def test_content_access_returns_none_when_permission_is_denied(tmp_path):
    access = make_access(tmp_path, read=False)

    assert access.read(make_item(tmp_path / "notes.txt")) is None


def test_content_access_returns_none_when_source_is_disabled(tmp_path):
    access = make_access(tmp_path, enabled=False)

    assert access.read(make_item(tmp_path / "notes.txt")) is None


def test_content_access_returns_none_for_path_outside_authorized_scope(tmp_path):
    authorized = tmp_path / "authorized"
    outside = tmp_path / "outside"
    authorized.mkdir()
    outside.mkdir()

    access = make_access(authorized)

    assert access.read(make_item(outside / "notes.txt")) is None


def test_content_access_returns_none_for_unindexed_content(tmp_path):
    access = make_access(tmp_path)

    assert access.read(make_item(tmp_path / "notes.txt")) is None

def test_content_access_resolves_equivalent_source_paths(tmp_path):
    from personal_ai.application.canonical_content_access import (
        LocalCanonicalContentAccess,
    )

    path = tmp_path / "notes.txt"
    alias_path = tmp_path / "nested" / ".." / "notes.txt"
    index = make_index(path.resolve())

    access = LocalCanonicalContentAccess(
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
        content_index=index,
    )

    item = make_item(
        alias_path,
        uri=path.resolve().as_uri(),
    )

    assert access.read(item) == "authorized document content"

def test_content_access_returns_none_when_content_hash_mismatches(tmp_path):
    path = tmp_path / "notes.txt"
    index = make_index(path)
    access = make_access(tmp_path)
    access.content_index = index

    item = make_item(path, content_hash="different-hash")

    assert access.read(item) is None
