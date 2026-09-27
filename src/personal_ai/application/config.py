from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from personal_ai.core.llm_config import (
    LLMProviderConfig,
    validate_llm_provider_config,
)
from personal_ai.filesystem.scope import FilesystemAccessScope
from personal_ai.permissions.policy import PermissionPolicy
from personal_ai.sources.config import SourceConfig


def _load_yaml(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"configuration file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if not isinstance(config, dict):
        raise ValueError(f"configuration must be a dictionary: {path}")

    return config


def _load_filesystem_scope(path: Path) -> FilesystemAccessScope:
    config = _load_yaml(path)
    authorized_roots = config.get("authorized_roots", [])

    if not isinstance(authorized_roots, list):
        raise ValueError(
            f"authorized_roots must be a list: {path}"
        )

    return FilesystemAccessScope(authorized_roots)


@dataclass(frozen=True)
class ApplicationConfig:
    permission_policy: PermissionPolicy
    source_config: SourceConfig
    llm_config: LLMProviderConfig
    filesystem_scope: FilesystemAccessScope

    @classmethod
    def from_paths(cls, paths: object) -> ApplicationConfig:
        permission_path = paths.permissions_config
        source_path = paths.sources_config
        llm_path = paths.llm_config
        filesystem_path = paths.filesystem_config

        permission_config = _load_yaml(permission_path)
        source_config = _load_yaml(source_path)
        llm_config = _load_yaml(llm_path)
        filesystem_scope = _load_filesystem_scope(filesystem_path)

        return cls(
            permission_policy=PermissionPolicy(permission_config),
            source_config=SourceConfig(source_config),
            llm_config=validate_llm_provider_config(llm_config),
            filesystem_scope=filesystem_scope,
        )