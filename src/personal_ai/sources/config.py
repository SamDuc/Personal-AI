from pathlib import Path

import yaml


class SourceConfig:
    def __init__(self, config: dict) -> None:
        if not isinstance(config, dict):
            raise ValueError("source config must be a dictionary")

        self.config = config

    @classmethod
    def from_file(cls, path: str | Path) -> "SourceConfig":
        config_path = Path(path)

        if not config_path.is_file():
            raise FileNotFoundError(f"source config not found: {config_path}")

        with config_path.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file)

        return cls(config)

    def get_source(self, source_id: str) -> dict:
        sources = self.config.get("sources", {})

        if not isinstance(sources, dict):
            raise ValueError("sources must be a dictionary")

        if source_id not in sources:
            raise KeyError(f"unknown source: {source_id}")

        source = sources[source_id]

        if not isinstance(source, dict):
            raise ValueError(f"invalid source configuration: {source_id}")

        return dict(source)
