from dataclasses import dataclass

from personal_ai.core.models import DataItem
from personal_ai.retrieval.local import RetrievalResult


@dataclass(frozen=True)
class SearchableContent:
    item: DataItem
    text: str


@dataclass(frozen=True)
class LocalSearchRequest:
    query: str
    limit: int = 10


def search_local_content(
    items: list[SearchableContent],
    request: LocalSearchRequest,
) -> list[RetrievalResult]:
    query = request.query.strip()

    if not query:
        raise ValueError("Search query must not be empty")

    if request.limit <= 0:
        raise ValueError("Search limit must be greater than zero")

    results: list[RetrievalResult] = []

    for searchable in items:
        item = searchable.item

        if item.source != "local_filesystem":
            continue

        if not item.searchable:
            continue

        if not item.content_available:
            continue

        if item.content_ref is None:
            continue

        if not item.access_policy.read:
            continue

        if query.casefold() not in searchable.text.casefold():
            continue

        results.append(RetrievalResult(item=item))

        if len(results) >= request.limit:
            break

    return results
