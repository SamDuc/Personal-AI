from datetime import UTC, datetime
from mimetypes import guess_type
from pathlib import Path

from personal_ai.connectors.local_filesystem import LocalFileMetadata


def discover_local_files(scope: Path) -> list[LocalFileMetadata]:
    """Discover files recursively within an explicit directory scope."""
    if not scope.exists():
        raise FileNotFoundError(scope)

    if not scope.is_dir():
        raise NotADirectoryError(scope)

    results: list[LocalFileMetadata] = []

    for path in scope.rglob("*"):
        if not path.is_file():
            continue

        stat = path.stat()
        mime_type, _ = guess_type(path.name)

        results.append(
            LocalFileMetadata(
                path=path,
                size=stat.st_size,
                created_at=datetime.fromtimestamp(stat.st_ctime, tz=UTC),
                modified_at=datetime.fromtimestamp(stat.st_mtime, tz=UTC),
                mime_type=mime_type,
            )
        )

    return results
