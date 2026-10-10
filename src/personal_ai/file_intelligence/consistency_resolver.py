"""Consistency resolution boundary for local filesystem indexed content."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from personal_ai.file_intelligence.consistency import (
    SourceSnapshot,
    snapshot_local_file,
)
from personal_ai.file_intelligence.index import IndexedContent

CONSISTENT = "consistent"
OUT_OF_SYNC = "out_of_sync"
SOURCE_MISSING = "source_missing"
SOURCE_UNAVAILABLE = "source_unavailable"


@dataclass(frozen=True)
class ConsistencyResult:
    """Result of an observational source/index consistency check."""

    state: str
    source_snapshot: SourceSnapshot | None


class ConsistencyResolver:
    """Resolve consistency without modifying source or index state."""

    def __init__(
        self,
        *,
        snapshotter: Callable[[str | Path], SourceSnapshot] = snapshot_local_file,
    ) -> None:
        self._snapshotter = snapshotter

    def resolve(
        self,
        indexed: IndexedContent,
        *,
        indexed_source_modified_at: datetime,
    ) -> ConsistencyResult:
        """Determine the consistency state of an indexed representation."""
        try:
            snapshot = self._snapshotter(indexed.source_path)
        except FileNotFoundError:
            return ConsistencyResult(
                state=SOURCE_MISSING,
                source_snapshot=None,
            )
        except (PermissionError, OSError, UnicodeError):
            return ConsistencyResult(
                state=SOURCE_UNAVAILABLE,
                source_snapshot=None,
            )

        indexed_source = str(Path(indexed.source_path).resolve())
        if indexed_source != snapshot.source_id:
            raise ValueError(
                "Indexed content source does not match source snapshot"
            )

        if (
            snapshot.content_hash is not None
            and indexed.content_hash != snapshot.content_hash
        ):
            return ConsistencyResult(
                state=OUT_OF_SYNC,
                source_snapshot=snapshot,
            )

        if indexed_source_modified_at == snapshot.modified_at:
            return ConsistencyResult(
                state=CONSISTENT,
                source_snapshot=snapshot,
            )

        return ConsistencyResult(
            state=OUT_OF_SYNC,
            source_snapshot=snapshot,
        )
