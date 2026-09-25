from pathlib import Path

import pytest

from personal_ai.connectors.local_content_index import index_extracted_content
from personal_ai.connectors.local_file_content_extraction import ExtractedContent
from personal_ai.retrieval.local_search import (
    LocalSearchRequest,
    SearchableContent,
    search_local_content,
)


def make_searchable_content(
    tmp_path: Path,
    text: str = "Personal AI project notes",
) -> SearchableContent:
    extracted = ExtractedContent(
        path=tmp_path / "notes.txt",
        text=text,
        content_hash="test-hash",
        content_available=True,
        extraction_version="1",
    )

    indexed = index_extracted_content(extracted)

    return SearchableContent(
        index=indexed,
        text=text,
    )


def test_search_returns_matching_content(tmp_path: Path) -> None:
    searchable = make_searchable_content(
        tmp_path,
        "Personal AI project architecture",
    )

    results = search_local_content(
        [searchable],
        LocalSearchRequest(query="architecture"),
    )

    assert len(results) == 1
    assert results[0].content_ref == searchable.index.content_ref


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

    indexed = index_extracted_content(
        ExtractedContent(
            path=tmp_path / "unsearchable" / "notes.txt",
            text="Personal AI architecture",
            content_hash="unsearchable-hash",
            content_available=True,
            extraction_version="1",
        )
    )

    unsearchable_index = indexed.__class__(
        content_ref=indexed.content_ref,
        content_hash=indexed.content_hash,
        content_available=indexed.content_available,
        searchable=False,
        embedding_ref=indexed.embedding_ref,
        indexed_at=indexed.indexed_at,
        sync_status=indexed.sync_status,
    )

    unsearchable = SearchableContent(
        index=unsearchable_index,
        text="Personal AI architecture",
    )

    results = search_local_content(
        [unsearchable, searchable],
        LocalSearchRequest(query="architecture"),
    )

    assert len(results) == 1
    assert results[0].content_ref == searchable.index.content_ref
def test_search_skips_unavailable_content(tmp_path: Path) -> None:
    searchable = make_searchable_content(
        tmp_path / "searchable",
        "Personal AI architecture",
    )

    unavailable_index = index_extracted_content(
        ExtractedContent(
            path=tmp_path / "unavailable" / "notes.txt",
            text="Personal AI architecture",
            content_hash="unavailable-hash",
            content_available=True,
            extraction_version="1",
        )
    )

    unavailable_index = unavailable_index.__class__(
        content_ref=unavailable_index.content_ref,
        content_hash=unavailable_index.content_hash,
        content_available=False,
        searchable=unavailable_index.searchable,
        embedding_ref=unavailable_index.embedding_ref,
        indexed_at=unavailable_index.indexed_at,
        sync_status=unavailable_index.sync_status,
    )

    unavailable = SearchableContent(
        index=unavailable_index,
        text="Personal AI architecture",
    )

    results = search_local_content(
        [unavailable, searchable],
        LocalSearchRequest(query="architecture"),
    )

    assert len(results) == 1
    assert results[0].content_ref == searchable.index.content_ref