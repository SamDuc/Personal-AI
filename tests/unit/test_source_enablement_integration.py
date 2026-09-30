from pathlib import Path

from personal_ai.connectors.local_file_source import discover_enabled_local_files
from personal_ai.sources.config import SourceConfig


def test_disabled_local_filesystem_source_stops_before_discovery(
    tmp_path: Path,
) -> None:
    config = SourceConfig(
        {
            "sources": {
                "local_filesystem": {
                    "enabled": False,
                }
            }
        }
    )

    result = discover_enabled_local_files(tmp_path, config)

    assert result == []


def test_enabled_local_filesystem_source_allows_discovery(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "example.txt"
    source_file.write_text("hello", encoding="utf-8")

    config = SourceConfig(
        {
            "sources": {
                "local_filesystem": {
                    "enabled": True,
                }
            }
        }
    )

    result = discover_enabled_local_files(tmp_path, config)

    assert len(result) == 1
    assert result[0].path == source_file
