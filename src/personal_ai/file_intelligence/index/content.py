"""Content index boundary."""

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from threading import RLock

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


@dataclass(frozen=True)
class ContentIndexSourceState:
    """Snapshot of index state for one source path."""

    source_path: str
    indexed: IndexedContent | None
    content_entries: tuple[tuple[tuple[str, str], str], ...]


class ContentIndex:
    """Thread-safe store of derived indexed representations."""

    def __init__(self) -> None:
        self._items: dict[str, IndexedContent] = {}
        self._content_by_ref: dict[tuple[str, str], str] = {}
        self._state_lock = RLock()
        self._source_locks_guard = RLock()
        self._source_locks: dict[str, RLock] = {}

    @staticmethod
    def _source_key(source_path: str) -> str:
        return str(Path(source_path).expanduser().resolve())

    def _get_source_lock(self, source_path: str) -> RLock:
        key = self._source_key(source_path)
        with self._source_locks_guard:
            lock = self._source_locks.get(key)
            if lock is None:
                lock = RLock()
                self._source_locks[key] = lock
            return lock

    @contextmanager
    def lock_source(self, source_path: str) -> Iterator[None]:
        """Serialize refreshes and index access for one source path."""
        with self._get_source_lock(source_path):
            yield

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
        if not isinstance(content.content_hash, str) or not content.content_hash.strip():
            raise ValueError("content_hash must not be empty")

        with self.lock_source(content.source_path), self._state_lock:
            indexed = IndexedContent(
                source_path=content.source_path,
                content_hash=content.content_hash,
                content_ref=content_ref,
                indexed_at=indexed_at,
                searchable=True,
                sync_status="indexed",
            )
            self._items[content.source_path] = indexed
            self._content_by_ref[(content_ref, content.source_path)] = (
                content.text
            )
            return indexed

    def get(self, source_path: str) -> IndexedContent | None:
        """Return the indexed representation for a source path."""
        with self.lock_source(source_path), self._state_lock:
            return self._items.get(source_path)

    def get_content(
        self,
        content_ref: str,
        *,
        source_path: str,
        content_hash: str,
    ) -> str | None:
        """Return content only when reference, source, and hash match."""
        with self.lock_source(source_path), self._state_lock:
            indexed = self._items.get(source_path)
            if indexed is None:
                return None
            if indexed.content_ref != content_ref:
                return None
            if indexed.content_hash != content_hash:
                return None
            return self._content_by_ref.get((content_ref, source_path))

    def capture_source_state(
        self,
        source_path: str,
    ) -> ContentIndexSourceState:
        """Capture all index state associated with one source path."""
        with self.lock_source(source_path), self._state_lock:
            return ContentIndexSourceState(
                source_path=source_path,
                indexed=self._items.get(source_path),
                content_entries=tuple(
                    (key, value)
                    for key, value in self._content_by_ref.items()
                    if key[1] == source_path
                ),
            )

    def restore_source_state(
        self,
        state: ContentIndexSourceState,
    ) -> None:
        """Restore the captured index state for one source path."""
        with self.lock_source(state.source_path), self._state_lock:
            for key in tuple(self._content_by_ref):
                if key[1] == state.source_path:
                    del self._content_by_ref[key]

            if state.indexed is None:
                self._items.pop(state.source_path, None)
            else:
                self._items[state.source_path] = state.indexed

            self._content_by_ref.update(dict(state.content_entries))
