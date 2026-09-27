from personal_ai.application.config import ApplicationConfig
from personal_ai.application.paths import ApplicationPaths


def test_application_config_loads_all_required_configs(tmp_path):
    config_dir = tmp_path / "config"
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
        "version: 1\nproviders:\n  fake:\n    enabled: true\n    type: local\n",
        encoding="utf-8",
    )
    (config_dir / "filesystem.yaml").write_text(
        "version: 1\nauthorized_roots: []\n",
        encoding="utf-8",
    )

    config = ApplicationConfig.from_paths(
        ApplicationPaths(config_dir=config_dir, data_dir=tmp_path / "data")
    )

    assert config.llm_config.version == 1
    assert config.llm_config.providers["fake"]["enabled"] is True
    assert config.filesystem_scope.authorized_roots == ()


def test_application_config_rejects_missing_llm_config(tmp_path):
    config_dir = tmp_path / "config"
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
    (config_dir / "filesystem.yaml").write_text(
        "version: 1\nauthorized_roots: []\n",
        encoding="utf-8",
    )

    try:
        ApplicationConfig.from_paths(
            ApplicationPaths(config_dir=config_dir, data_dir=tmp_path / "data")
        )
    except FileNotFoundError as exc:
        assert "llm.yaml" in str(exc)
    else:
        raise AssertionError("Expected missing llm.yaml to fail")