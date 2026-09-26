from pathlib import Path

import pytest

from personal_ai.sources.config import SourceConfig

SOURCES_PATH = Path("config/sources/sources.yaml")


def test_source_config_loads_local_filesystem_source() -> None:
    config = SourceConfig.from_file(SOURCES_PATH)

    source = config.get_source("local_filesystem")

    assert source["enabled"] is False
    assert source["type"] == "local_filesystem"
    assert source["access_mode"] == "read_only"


def test_source_config_rejects_unknown_source() -> None:
    config = SourceConfig.from_file(SOURCES_PATH)

    with pytest.raises(KeyError):
        config.get_source("unknown_source")

def test_source_config_reports_local_filesystem_disabled() -> None:
    config = SourceConfig.from_file(SOURCES_PATH)

    assert config.is_enabled("local_filesystem") is False
