from personal_ai.application.bootstrap import bootstrap
from personal_ai.application.paths import ApplicationPaths


def test_bootstrap_constructs_application_boundary(tmp_path):
    paths = ApplicationPaths(
        config_dir=__import__("pathlib").Path("config"),
        data_dir=tmp_path / "data",
    )

    application = bootstrap(paths)

    assert application.config.llm_config.providers["fake"]["enabled"] is True
    assert application.permission_evaluator.evaluate("local_filesystem", "read") == "denied"
    assert application.agent is not None


def test_bootstrap_rejects_unknown_provider(monkeypatch):
    monkeypatch.setenv("PERSONAL_AI_LLM_PROVIDER", "unknown")

    try:
        bootstrap(
            ApplicationPaths(
                config_dir=__import__("pathlib").Path("config"),
                data_dir=__import__("pathlib").Path("data"),
            )
        )
    except ValueError as exc:
        assert "Unknown provider" in str(exc)
    else:
        raise AssertionError("Expected unknown provider to fail")


def test_bootstrap_injects_local_retriever(tmp_path):
    application = bootstrap(
        ApplicationPaths(
            config_dir=__import__("pathlib").Path("config"),
            data_dir=tmp_path / "data",
        )
    )

    assert application.agent.retriever is not None

def test_bootstrap_registers_general_agent_route(tmp_path):
    from pathlib import Path

    application = bootstrap(
        ApplicationPaths(
            config_dir=Path("config"),
            data_dir=tmp_path / "data",
        )
    )

    assert application.agent_router.route_ids == ("general",)
    assert application.agent_router.resolve("general") is application.agent


def test_bootstrap_selects_configured_openai_compatible_provider(monkeypatch, tmp_path):
    import shutil
    from pathlib import Path

    monkeypatch.setenv("PERSONAL_AI_LLM_PROVIDER", "my_llm")

    config_dir = tmp_path / "config"
    (config_dir / "permissions").mkdir(parents=True)
    (config_dir / "sources").mkdir(parents=True)

    source_config = Path("config/llm.yaml").read_text(encoding="utf-8")
    enabled_config = source_config.replace(
        "  my_llm:\n    enabled: false",
        "  my_llm:\n    enabled: true",
    )
    (config_dir / "llm.yaml").write_text(
        enabled_config,
        encoding="utf-8",
    )

    shutil.copy2(
        Path("config/permissions/permissions.yaml"),
        config_dir / "permissions/permissions.yaml",
    )
    shutil.copy2(
        Path("config/sources/sources.yaml"),
        config_dir / "sources/sources.yaml",
    )
    shutil.copy2(
        Path("config/filesystem.yaml"),
        config_dir / "filesystem.yaml",
    )

    application = bootstrap(
        ApplicationPaths(
            config_dir=config_dir,
            data_dir=tmp_path / "data",
        )
    )

    provider = application.agent.integration.runtime.provider

    from personal_ai.core.openai_compatible import OpenAICompatibleProvider

    assert isinstance(provider, OpenAICompatibleProvider)
