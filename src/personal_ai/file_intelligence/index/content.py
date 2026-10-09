"""Content index boundary."""

from dataclasses import dataclass

from personal_ai.file_intelligence.normalization import NormalizedContent


@dataclass(frozen=True)
class IndexedContent:
    """Derived representation of normalized content."""

    source_path: str
    content_hash: str
    content_ref: str
    indexed_at: str
    searchable: bool
    sync_status: str


class ContentIndex:
    """Store derived indexed representations."""

    def __init__(self) -> None:
        self._items: dict[str, IndexedContent] = {}
        self._content_by_ref: dict[tuple[str, str], str] = {}

    def index(
        self,
        content: NormalizedContent,
        *,
        content_ref: str,
        indexed_at: str,
    ) -> IndexedContent:
        """Index already-normalized content."""
        if not content_ref:
            raise ValueError("content_ref must not be empty")
        if not indexed_at:
            raise ValueError("indexed_at must not be empty")

        indexed = IndexedContent(
            source_path=content.source_path,
            content_hash=content.content_hash,
            content_ref=content_ref,
            indexed_at=indexed_at,
            searchable=True,
            sync_status="indexed",
        )
        self._items[content.source_path] = indexed
        self._content_by_ref[(content_ref, content.source_path)] = content.text
        return indexed

    def get(self, source_path: str) -> IndexedContent | None:
        """Return the indexed representation for a source path."""
        return self._items.get(source_path)

    def get_content(
        self,
        content_ref: str,
        *,
        source_path: str,
        content_hash: str,
    ) -> str | None:
        """Return content only when reference, source, and hash match."""
        indexed = self._items.get(source_path)

        if indexed is None:
            return None

        if indexed.content_ref != content_ref:
            return None

        if indexed.content_hash != content_hash:
            return None

        return self._content_by_ref.get((content_ref, source_path))
