from pathlib import Path

import pytest

from personal_ai.connectors.local_file_source import discover_enabled_local_files
from personal_ai.sources.config import SourceConfig

SOURCES_PATH = Path("config/sources/sources.yaml")


def test_disabled_local_filesystem_source_does_not_discover(
    tmp_path: Path,
) -> None:
    config = SourceConfig.from_file(SOURCES_PATH)

    results = discover_enabled_local_files(tmp_path, config)

    assert results == []


def test_enabled_local_filesystem_source_discovers_files(
    tmp_path: Path,
) -> None:
    (tmp_path / "example.txt").write_text("hello", encoding="utf-8")

    config = SourceConfig(
        {
            "sources": {
                "local_filesystem": {
                    "enabled": True,
                }
            }
        }
    )

    results = discover_enabled_local_files(tmp_path, config)

    assert len(results) == 1
    assert results[0].path == tmp_path / "example.txt"


def test_enabled_local_filesystem_source_propagates_missing_scope_error(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "does-not-exist"

    config = SourceConfig(
        {
            "sources": {
                "local_filesystem": {
                    "enabled": True,
                }
            }
        }
    )

    with pytest.raises(FileNotFoundError):
        discover_enabled_local_files(missing, config)

def test_enabled_local_filesystem_source_propagates_file_scope_error(
    tmp_path: Path,
) -> None:
    file_scope = tmp_path / "paper.pdf"
    file_scope.write_bytes(b"pdf")

    config = SourceConfig(
        {
            "sources": {
                "local_filesystem": {
                    "enabled": True,
                }
            }
        }
    )

    with pytest.raises(NotADirectoryError):
        discover_enabled_local_files(file_scope, config)
