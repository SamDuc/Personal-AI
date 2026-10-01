from personal_ai.core.models import AccessPolicy, DataItem
from personal_ai.retrieval.local import (
    RetrievalRequest,
    retrieve_local_items,
)


def make_item(*, sync_status: str = "indexed") -> DataItem:
    return DataItem(
        id="local-consistency",
        source="local_filesystem",
        source_id="example.txt",
        uri="file:///example.txt",
        item_type="file",
        content_available=True,
        content_ref="index://content/example",
        content_hash="sha256:test",
        searchable=True,
        sync_status=sync_status,
        access_policy=AccessPolicy(read=True, write=False),
    )


def test_retrieval_accepts_consistent_indexed_item() -> None:
    item = make_item(sync_status="indexed")

    results = retrieve_local_items(
        [item],
        RetrievalRequest(query="example"),
    )

    assert len(results) == 1
    assert results[0].item is item


def test_retrieval_rejects_out_of_sync_item() -> None:
    item = make_item(sync_status="out_of_sync")

    results = retrieve_local_items(
        [item],
        RetrievalRequest(query="example"),
    )

    assert results == []


def test_retrieval_rejects_missing_source_item() -> None:
    item = make_item(sync_status="source_missing")

    results = retrieve_local_items(
        [item],
        RetrievalRequest(query="example"),
    )

    assert results == []


def test_retrieval_rejects_unavailable_source_item() -> None:
    item = make_item(sync_status="source_unavailable")

    results = retrieve_local_items(
        [item],
        RetrievalRequest(query="example"),
    )

    assert results == []


def test_retrieval_consistency_regression_does_not_modify_item() -> None:
    item = make_item(sync_status="out_of_sync")
    original = (
        item.content_available,
        item.content_ref,
        item.content_hash,
        item.searchable,
        item.sync_status,
        item.access_policy,
    )

    results = retrieve_local_items(
        [item],
        RetrievalRequest(query="example"),
    )

    assert results == []
    assert (
        item.content_available,
        item.content_ref,
        item.content_hash,
        item.searchable,
        item.sync_status,
        item.access_policy,
    ) == original
