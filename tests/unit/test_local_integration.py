from pathlib import Path

import pytest

from personal_ai.connectors.local_file_content_extraction import ExtractedContent
from personal_ai.core.models import AccessPolicy, DataItem
from personal_ai.retrieval.local_integration import integrate_local_content_index


def make_item(path: Path) -> DataItem:
    return DataItem(
        id="local-1",
        source="local_filesystem",
        source_id=str(path),
        uri=path.resolve().as_uri(),
        item_type="file",
        content_available=False,
        content_ref=None,
        content_hash=None,
        searchable=False,
        access_policy=AccessPolicy(read=True, write=False),
        sensitivity="private",
    )


def make_extracted(path: Path) -> ExtractedContent:
    return ExtractedContent(
        path=path,
        text="Hello Personal AI",
        content_hash="test-hash",
        content_available=True,
        extraction_version="1",
    )


def test_integration_updates_index_fields(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    item = make_item(path)
    extracted = make_extracted(path)

    result = integrate_local_content_index(item, extracted)

    assert result.content_available is True
    assert result.content_ref is not None
    assert result.content_ref.startswith("index://content/")
    assert result.content_hash == "test-hash"
    assert result.searchable is True
    assert result.indexed_at is not None
    assert result.sync_status == "indexed"


def test_integration_preserves_source_identity(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    item = make_item(path)
    extracted = make_extracted(path)

    result = integrate_local_content_index(item, extracted)

    assert result.id == item.id
    assert result.source == item.source
    assert result.source_id == item.source_id
    assert result.uri == item.uri


def test_integration_preserves_access_policy(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    item = make_item(path)
    extracted = make_extracted(path)

    original_policy = item.access_policy

    result = integrate_local_content_index(item, extracted)

    assert result.access_policy is original_policy
    assert result.access_policy.read is True
    assert result.access_policy.write is False


def test_integration_preserves_sensitivity(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    item = make_item(path)
    extracted = make_extracted(path)

    result = integrate_local_content_index(item, extracted)

    assert result.sensitivity == "private"


def test_integration_rejects_non_local_source(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    item = make_item(path)
    item.source = "google_drive"
    extracted = make_extracted(path)

    with pytest.raises(ValueError, match="local_filesystem"):
        integrate_local_content_index(item, extracted)


def test_integration_rejects_mismatched_source_path(tmp_path: Path) -> None:
    item_path = tmp_path / "notes.txt"
    extracted_path = tmp_path / "other.txt"

    item = make_item(item_path)
    extracted = make_extracted(extracted_path)

    with pytest.raises(ValueError, match="does not match"):
        integrate_local_content_index(item, extracted)


def test_integration_propagates_unavailable_content_error(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    item = make_item(path)
    extracted = ExtractedContent(
        path=path,
        text="",
        content_hash="test-hash",
        content_available=False,
        extraction_version="1",
    )

    with pytest.raises(ValueError, match="content"):
        integrate_local_content_index(item, extracted)

def test_integration_preserves_utc_aware_indexed_at(
    tmp_path: Path,
) -> None:
    path = tmp_path / "notes.txt"
    item = make_item(path)
    extracted = make_extracted(path)

    result = integrate_local_content_index(item, extracted)

    assert result.indexed_at is not None
    assert result.indexed_at.tzinfo is not None
    assert result.indexed_at.utcoffset() is not None
