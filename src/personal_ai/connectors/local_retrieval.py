from dataclasses import dataclass

from personal_ai.core.models import DataItem


@dataclass(frozen=True)
class RetrievalRequest:
    query: str
    source: str | None = None
    limit: int = 10


@dataclass(frozen=True)
class RetrievalResult:
    item: DataItem


def retrieve_local_items(
    items: list[DataItem],
    request: RetrievalRequest,
) -> list[RetrievalResult]:
    if not request.query.strip():
        raise ValueError("Retrieval query must not be empty")

    if request.limit <= 0:
        raise ValueError("Retrieval limit must be greater than zero")

    results: list[RetrievalResult] = []

    for item in items:
        if item.source != "local_filesystem":
            continue
        if request.source is not None and item.source != request.source:
            continue
        if not item.searchable:
            continue
        if not item.content_available:
            continue
        if item.content_ref is None:
            continue
        if not item.access_policy.read:
            continue

        results.append(RetrievalResult(item=item))

        if len(results) >= request.limit:
            break

    return results
