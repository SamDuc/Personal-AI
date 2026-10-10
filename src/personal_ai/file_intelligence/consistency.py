"""Source snapshot boundary for local filesystem consistency."""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class SourceSnapshot:
    source: str
    source_id: str
    modified_at: datetime
    size: int | None = None
    modified_at_ns: int | None = None
    changed_at_ns: int | None = None


def snapshot_local_file(source_path: str | Path) -> SourceSnapshot:
    """Capture the authoritative local filesystem modification timestamp."""
    path = Path(source_path)

    if not path.exists():
        raise FileNotFoundError(path)

    if not path.is_file():
        raise ValueError(f"Source is not a regular file: {path}")

    stat = path.stat()

    return SourceSnapshot(
        source="local_filesystem",
        source_id=str(path.resolve()),
        modified_at=datetime.fromtimestamp(stat.st_mtime, tz=UTC),
        size=stat.st_size,
        modified_at_ns=stat.st_mtime_ns,
        changed_at_ns=stat.st_ctime_ns,
    )
