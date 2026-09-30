from pathlib import Path

import pytest

from personal_ai.core.models import AccessPolicy, DataItem
from personal_ai.retrieval.local import (
    RetrievalRequest,
    RetrievalResult,
    retrieve_local_items,
)


def make_item(
    *,
    source: str = "local_filesystem",
    searchable: bool = True,
    content_available: bool = True,
    content_ref: str | None = "local://example.txt",
    read: bool = True,
) -> DataItem:
    return DataItem(
        id="item-1",
        source=source,
        source_id=str(Path("example.txt")),
        uri="file:///example.txt",
        item_type="file",
        mime_type="text/plain",
        extension=".txt",
        name="example.txt",
        size=10,
        content_available=content_available,
        content_ref=content_ref,
        searchable=searchable,
        access_policy=AccessPolicy(
            read=read,
            write=False,
        ),
    )


def test_retrieval_returns_eligible_local_item() -> None:
    item = make_item()

    results = retrieve_local_items(
        [item],
        RetrievalRequest(query="example"),
    )

    assert len(results) == 1
    assert isinstance(results[0], RetrievalResult)
    assert results[0].item is item


def test_retrieval_rejects_non_local_source() -> None:
    item = make_item(source="other_source")

    results = retrieve_local_items(
        [item],
        RetrievalRequest(query="example"),
    )

    assert results == []


def test_retrieval_rejects_non_searchable_item() -> None:
    item = make_item(searchable=False)

    results = retrieve_local_items(
        [item],
        RetrievalRequest(query="example"),
    )

    assert results == []


def test_retrieval_rejects_content_unavailable() -> None:
    item = make_item(content_available=False)

    results = retrieve_local_items(
        [item],
        RetrievalRequest(query="example"),
    )

    assert results == []


def test_retrieval_rejects_missing_content_ref() -> None:
    item = make_item(content_ref=None)

    results = retrieve_local_items(
        [item],
        RetrievalRequest(query="example"),
    )

    assert results == []


def test_retrieval_rejects_read_denied_item() -> None:
    item = make_item(read=False)

    results = retrieve_local_items(
        [item],
        RetrievalRequest(query="example"),
    )

    assert results == []


def test_retrieval_respects_limit() -> None:
    first = make_item()
    second = DataItem(
        id="item-2",
        source=first.source,
        source_id="second.txt",
        uri="file:///second.txt",
        item_type="file",
        mime_type="text/plain",
        extension=".txt",
        name="second.txt",
        size=10,
        content_available=True,
        content_ref="local://second.txt",
        searchable=True,
        access_policy=AccessPolicy(
            read=True,
            write=False,
        ),
    )

    results = retrieve_local_items(
        [first, second],
        RetrievalRequest(query="example", limit=1),
    )

    assert len(results) == 1
    assert results[0].item is first


def test_retrieval_rejects_empty_query() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        retrieve_local_items(
            [make_item()],
            RetrievalRequest(query="   "),
        )


def test_retrieval_rejects_non_positive_limit() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        retrieve_local_items(
            [make_item()],
            RetrievalRequest(query="example", limit=0),
        )


def test_retrieval_does_not_modify_item_permissions() -> None:
    item = make_item(read=True)
    original_policy = item.access_policy

    retrieve_local_items(
        [item],
        RetrievalRequest(query="example"),
    )

    assert item.access_policy is original_policy
    assert item.access_policy.read is True
    assert item.access_policy.write is False
