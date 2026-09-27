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