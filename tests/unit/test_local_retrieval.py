from personal_ai.connectors.local_retrieval import (
    RetrievalRequest,
    RetrievalResult,
    retrieve_local_items,
)
from personal_ai.core.models import AccessPolicy, DataItem


def make_item(
    *,
    item_id: str = "local-1",
    searchable: bool = True,
    content_available: bool = True,
    content_ref: str | None = "index://content/local-1",
    read: bool = True,
    source: str = "local_filesystem",
) -> DataItem:
    return DataItem(
        id=item_id,
        source=source,
        source_id=item_id,
        uri=f"file:///C:/{item_id}.txt",
        item_type="file",
        content_available=content_available,
        content_ref=content_ref,
        searchable=searchable,
        access_policy=AccessPolicy(read=read),
    )


def test_retrieval_returns_eligible_local_items() -> None:
    item = make_item()

    results = retrieve_local_items(
        [item],
        RetrievalRequest(query="hello"),
    )

    assert len(results) == 1
    assert isinstance(results[0], RetrievalResult)
    assert results[0].item.id == item.id


def test_retrieval_rejects_unsearchable_items() -> None:
    item = make_item(searchable=False)

    results = retrieve_local_items(
        [item],
        RetrievalRequest(query="hello"),
    )

    assert results == []


def test_retrieval_rejects_items_without_content() -> None:
    item = make_item(content_available=False)

    results = retrieve_local_items(
        [item],
        RetrievalRequest(query="hello"),
    )

    assert results == []


def test_retrieval_rejects_items_without_content_ref() -> None:
    item = make_item(content_ref=None)

    results = retrieve_local_items(
        [item],
        RetrievalRequest(query="hello"),
    )

    assert results == []


def test_retrieval_respects_read_permission() -> None:
    item = make_item(read=False)

    results = retrieve_local_items(
        [item],
        RetrievalRequest(query="hello"),
    )

    assert results == []


def test_retrieval_does_not_return_non_local_sources() -> None:
    item = make_item(source="google_drive")

    results = retrieve_local_items(
        [item],
        RetrievalRequest(query="hello"),
    )

    assert results == []


def test_retrieval_respects_limit() -> None:
    items = [
        make_item(item_id="local-1"),
        make_item(item_id="local-2"),
        make_item(item_id="local-3"),
    ]

    results = retrieve_local_items(
        items,
        RetrievalRequest(query="hello", limit=2),
    )

    assert [result.item.id for result in results] == [
        "local-1",
        "local-2",
    ]


def test_retrieval_rejects_empty_query() -> None:
    try:
        retrieve_local_items(
            [make_item()],
            RetrievalRequest(query=" "),
        )
    except ValueError as exc:
        assert "query" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")


def test_retrieval_rejects_non_positive_limit() -> None:
    try:
        retrieve_local_items(
            [make_item()],
            RetrievalRequest(query="hello", limit=0),
        )
    except ValueError as exc:
        assert "limit" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")
