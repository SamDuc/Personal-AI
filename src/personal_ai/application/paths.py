from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path


def _default_data_dir() -> Path:
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA")
        if base:
            return Path(base) / "PersonalAI"

    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home) / "personal-ai"

    return Path.home() / ".local" / "share" / "personal-ai"


@dataclass(frozen=True)
class ApplicationPaths:
    """Explicit runtime paths; path resolution does not create files."""

    config_dir: Path
    data_dir: Path

    def __post_init__(self) -> None:
        object.__setattr__(self, "config_dir", Path(self.config_dir).expanduser().resolve())
        object.__setattr__(self, "data_dir", Path(self.data_dir).expanduser().resolve())

    @classmethod
    def from_environment(cls) -> ApplicationPaths:
        config_dir = Path(
            os.environ.get("PERSONAL_AI_CONFIG_DIR", str(Path.cwd() / "config"))
        )
        data_dir = Path(
            os.environ.get("PERSONAL_AI_DATA_DIR", str(_default_data_dir()))
        )
        return cls(config_dir=config_dir, data_dir=data_dir)

    @property
    def permissions_config(self) -> Path:
        return self.config_dir / "permissions" / "permissions.yaml"

    @property
    def sources_config(self) -> Path:
        return self.config_dir / "sources" / "sources.yaml"

    @property
    def llm_config(self) -> Path:
        return self.config_dir / "llm.yaml"
    @property
    def filesystem_config(self) -> Path:
       return self.config_dir / "filesystem.yaml"
