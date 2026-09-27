
from personal_ai.application.paths import ApplicationPaths


def test_from_environment_uses_explicit_config_directory(monkeypatch, tmp_path):
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"

    monkeypatch.setenv("PERSONAL_AI_CONFIG_DIR", str(config_dir))
    monkeypatch.setenv("PERSONAL_AI_DATA_DIR", str(data_dir))

    paths = ApplicationPaths.from_environment()

    assert paths.config_dir == config_dir.resolve()
    assert paths.data_dir == data_dir.resolve()


def test_paths_do_not_create_directories(monkeypatch, tmp_path):
    config_dir = tmp_path / "missing-config"
    data_dir = tmp_path / "missing-data"

    monkeypatch.setenv("PERSONAL_AI_CONFIG_DIR", str(config_dir))
    monkeypatch.setenv("PERSONAL_AI_DATA_DIR", str(data_dir))

    ApplicationPaths.from_environment()

    assert not config_dir.exists()
    assert not data_dir.exists()


def test_config_file_paths_are_under_config_directory(tmp_path):
    paths = ApplicationPaths(
        config_dir=tmp_path / "config",
        data_dir=tmp_path / "data",
    )

    assert paths.permissions_config == paths.config_dir / "permissions" / "permissions.yaml"
    assert paths.sources_config == paths.config_dir / "sources" / "sources.yaml"
    assert paths.llm_config == paths.config_dir / "llm.yaml"
