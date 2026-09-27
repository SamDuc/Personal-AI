from pathlib import Path

import pytest
import yaml

from personal_ai.application.config import ApplicationConfig
from personal_ai.application.paths import ApplicationPaths
from personal_ai.permissions.policy import PermissionPolicy
from personal_ai.sources.config import SourceConfig


def write_yaml(path: Path, content: object) -> None:
    path.write_text(
        yaml.safe_dump(content, sort_keys=False),
        encoding="utf-8",
    )


def test_source_config_rejects_non_dictionary_file(tmp_path: Path) -> None:
    path = tmp_path / "sources.yaml"
    write_yaml(path, ["invalid"])

    with pytest.raises(ValueError, match="source config must be a dictionary"):
        SourceConfig.from_file(path)


def test_source_config_rejects_non_dictionary_sources(tmp_path: Path) -> None:
    path = tmp_path / "sources.yaml"
    write_yaml(path, {"version": 1, "sources": []})

    config = SourceConfig.from_file(path)

    with pytest.raises(ValueError, match="sources must be a dictionary"):
        config.get_source("local_filesystem")


def test_source_config_rejects_non_dictionary_source_entry(
    tmp_path: Path,
) -> None:
    path = tmp_path / "sources.yaml"
    write_yaml(
        path,
        {
            "version": 1,
            "sources": {"local_filesystem": ["invalid"]},
        },
    )

    config = SourceConfig.from_file(path)

    with pytest.raises(ValueError, match="invalid source configuration"):
        config.get_source("local_filesystem")


def test_source_config_treats_missing_enabled_as_disabled(
    tmp_path: Path,
) -> None:
    path = tmp_path / "sources.yaml"
    write_yaml(
        path,
        {
            "version": 1,
            "sources": {"local_filesystem": {"type": "local_filesystem"}},
        },
    )

    config = SourceConfig.from_file(path)

    assert config.is_enabled("local_filesystem") is False


def test_source_config_requires_boolean_true_for_enabled(
    tmp_path: Path,
) -> None:
    path = tmp_path / "sources.yaml"
    write_yaml(
        path,
        {
            "version": 1,
            "sources": {
                "local_filesystem": {
                    "enabled": "true",
                }
            },
        },
    )

    config = SourceConfig.from_file(path)

    assert config.is_enabled("local_filesystem") is False


def test_permission_policy_rejects_non_dictionary_file(
    tmp_path: Path,
) -> None:
    path = tmp_path / "permissions.yaml"
    write_yaml(path, ["invalid"])

    with pytest.raises(ValueError, match="policy must be a dictionary"):
        PermissionPolicy.from_file(path)


def test_permission_policy_rejects_non_dictionary_defaults(
    tmp_path: Path,
) -> None:
    path = tmp_path / "permissions.yaml"
    write_yaml(
        path,
        {
            "version": 1,
            "defaults": [],
            "confirmation_required": [],
        },
    )

    policy = PermissionPolicy.from_file(path)

    with pytest.raises(
        ValueError,
        match="permission defaults must be a dictionary",
    ):
        policy.get_defaults()


def test_permission_policy_rejects_non_list_confirmation_operations(
    tmp_path: Path,
) -> None:
    path = tmp_path / "permissions.yaml"
    write_yaml(
        path,
        {
            "version": 1,
            "defaults": {},
            "confirmation_required": "delete",
        },
    )

    policy = PermissionPolicy.from_file(path)

    with pytest.raises(
        ValueError,
        match="confirmation_required must be a list",
    ):
        policy.get_confirmation_required()


def make_application_config_files(config_dir: Path) -> None:
    (config_dir / "permissions").mkdir(parents=True)
    (config_dir / "sources").mkdir(parents=True)

    (config_dir / "permissions" / "permissions.yaml").write_text(
        "version: 1\ndefaults: {}\nconfirmation_required: []\n",
        encoding="utf-8",
    )

    (config_dir / "sources" / "sources.yaml").write_text(
        "version: 1\nsources: {}\n",
        encoding="utf-8",
    )

    (config_dir / "llm.yaml").write_text(
        "version: 1\nproviders:\n"
        "  fake:\n"
        "    enabled: true\n"
        "    type: local\n",
        encoding="utf-8",
    )


def test_application_config_rejects_non_list_authorized_roots(
    tmp_path: Path,
) -> None:
    config_dir = tmp_path / "config"
    make_application_config_files(config_dir)

    (config_dir / "filesystem.yaml").write_text(
        "version: 1\nauthorized_roots: invalid\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="authorized_roots must be a list"):
        ApplicationConfig.from_paths(
            ApplicationPaths(
                config_dir=config_dir,
                data_dir=tmp_path / "data",
            )
        )
