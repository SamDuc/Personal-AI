from dataclasses import dataclass

from personal_ai.connectors.local_content_index import LocalContentIndex


@dataclass(frozen=True)
class SearchableContent:
    index: LocalContentIndex
    text: str


@dataclass(frozen=True)
class LocalSearchRequest:
    query: str
    limit: int = 10


def search_local_content(
    items: list[SearchableContent],
    request: LocalSearchRequest,
) -> list[LocalContentIndex]:
    query = request.query.strip()

    if not query:
        raise ValueError("Search query must not be empty")

    if request.limit <= 0:
        raise ValueError("Search limit must be greater than zero")

    results: list[LocalContentIndex] = []

    for item in items:
        if not item.index.searchable:
            continue

        if not item.index.content_available:
            continue

        if query.casefold() not in item.text.casefold():
            continue

        results.append(item.index)

        if len(results) >= request.limit:
            break

    return results
