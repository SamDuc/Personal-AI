from pathlib import Path

import demo_chat


def test_create_application_uses_environment_config_directory(
    monkeypatch,
    tmp_path,
):
    config_dir = tmp_path / "config"
    captured = {}

    def fake_bootstrap(paths):
        captured["paths"] = paths
        return object()

    monkeypatch.setenv("PERSONAL_AI_CONFIG_DIR", str(config_dir))
    monkeypatch.setattr(demo_chat, "bootstrap", fake_bootstrap)

    application = demo_chat.create_application()

    assert application is not None
    assert captured["paths"].config_dir == config_dir.resolve()
    assert captured["paths"].data_dir == demo_chat.DATA_DIR.resolve()


def test_create_application_defaults_to_project_config(monkeypatch):
    captured = {}

    def fake_bootstrap(paths):
        captured["paths"] = paths
        return object()

    monkeypatch.delenv("PERSONAL_AI_CONFIG_DIR", raising=False)
    monkeypatch.setattr(demo_chat, "bootstrap", fake_bootstrap)

    demo_chat.create_application()

    assert captured["paths"].config_dir == Path("config").resolve()
    assert captured["paths"].data_dir == demo_chat.DATA_DIR.resolve()
