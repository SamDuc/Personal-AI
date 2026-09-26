from pathlib import Path

from personal_ai.connectors.local_content_index import index_extracted_content
from personal_ai.connectors.local_file_content_extraction import ExtractedContent
from personal_ai.core.models import AccessPolicy, DataItem
from personal_ai.retrieval.local_search import (
    LocalSearchRequest,
    SearchableContent,
    search_local_content,
)


def make_searchable_content(
    tmp_path: Path,
    text: str = "Personal AI project notes",
    read: bool = True,
) -> SearchableContent:
    extracted = ExtractedContent(
        path=tmp_path / "notes.txt",
        text=text,
        content_hash="test-hash",
        content_available=True,
        extraction_version="1",
    )

    indexed = index_extracted_content(extracted)

    item = DataItem(
        id=f"local:{extracted.path}",
        source="local_filesystem",
        source_id=str(extracted.path),
        uri=extracted.path.resolve().as_uri(),
        item_type="file",
        content_available=indexed.content_available,
        content_ref=indexed.content_ref,
        content_hash=indexed.content_hash,
        searchable=indexed.searchable,
        access_policy=AccessPolicy(read=read),
    )

    return SearchableContent(
        item=item,
        text=text,
    )


def test_search_returns_matching_authorized_content(tmp_path: Path) -> None:
    searchable = make_searchable_content(
        tmp_path,
        "Personal AI project architecture",
    )

    results = search_local_content(
        [searchable],
        LocalSearchRequest(query="architecture"),
    )

    assert len(results) == 1
    assert results[0].item.id == searchable.item.id
    assert results[0].item.content_ref == searchable.item.content_ref


def test_search_rejects_unreadable_item(tmp_path: Path) -> None:
    searchable = make_searchable_content(
        tmp_path,
        "Personal AI project architecture",
        read=False,
    )

    results = search_local_content(
        [searchable],
        LocalSearchRequest(query="architecture"),
    )

    assert results == []


def test_search_preserves_canonical_data_item(tmp_path: Path) -> None:
    searchable = make_searchable_content(
        tmp_path,
        "Personal AI project architecture",
    )

    searchable.item.sensitivity = "private"

    results = search_local_content(
        [searchable],
        LocalSearchRequest(query="architecture"),
    )

    assert len(results) == 1
    result_item = results[0].item

    assert result_item.id == searchable.item.id
    assert result_item.source == searchable.item.source
    assert result_item.source_id == searchable.item.source_id
    assert result_item.uri == searchable.item.uri
    assert result_item.content_ref == searchable.item.content_ref
    assert result_item.content_hash == searchable.item.content_hash
    assert result_item.sensitivity == "private"
    assert result_item.access_policy.read is True


def test_search_does_not_return_non_matching_content(tmp_path: Path) -> None:
    searchable = make_searchable_content(
        tmp_path,
        "Personal AI project architecture",
    )

    results = search_local_content(
        [searchable],
        LocalSearchRequest(query="raspberry"),
    )

    assert results == []


def test_search_rejects_empty_query(tmp_path: Path) -> None:
    searchable = make_searchable_content(tmp_path)

    import pytest

    with pytest.raises(ValueError, match="query"):
        search_local_content(
            [searchable],
            LocalSearchRequest(query=" "),
        )


def test_search_respects_limit(tmp_path: Path) -> None:
    first = make_searchable_content(
        tmp_path / "first",
        "Personal AI architecture",
    )
    second = make_searchable_content(
        tmp_path / "second",
        "Personal AI retrieval architecture",
    )

    results = search_local_content(
        [first, second],
        LocalSearchRequest(query="architecture", limit=1),
    )

    assert len(results) == 1


def test_search_skips_unsearchable_content(tmp_path: Path) -> None:
    searchable = make_searchable_content(
        tmp_path / "searchable",
        "Personal AI architecture",
    )

    searchable.item.searchable = False

    results = search_local_content(
        [searchable],
        LocalSearchRequest(query="architecture"),
    )

    assert results == []


def test_search_skips_unavailable_content(tmp_path: Path) -> None:
    searchable = make_searchable_content(
        tmp_path / "unavailable",
        "Personal AI architecture",
    )

    searchable.item.content_available = False

    results = search_local_content(
        [searchable],
        LocalSearchRequest(query="architecture"),
    )

    assert results == []
