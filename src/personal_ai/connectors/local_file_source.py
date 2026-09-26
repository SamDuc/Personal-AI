from pathlib import Path

from personal_ai.connectors.local_file_discovery import (
    LocalFileMetadata,
    discover_local_files,
)
from personal_ai.sources.config import SourceConfig


def discover_enabled_local_files(
    scope: Path,
    source_config: SourceConfig,
) -> list[LocalFileMetadata]:
    """Discover local files only when the local filesystem source is enabled."""
    if not source_config.is_enabled("local_filesystem"):
        return []

    return discover_local_files(scope)
