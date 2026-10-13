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


def test_bootstrap_injects_canonical_retrieval(tmp_path):
    from personal_ai.application.canonical_retriever import (
        LocalCanonicalRetrieval,
    )

    application = bootstrap(
        ApplicationPaths(
            config_dir=__import__("pathlib").Path("config"),
            data_dir=tmp_path / "data",
        )
    )

    assert isinstance(
        application.agent.retrieval,
        LocalCanonicalRetrieval,
    )

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
    ).replace(
        "  my_llm:\n    enabled: true\n    type: local",
        "  my_llm:\n    enabled: true\n    type: cloud",
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

    from personal_ai.core.cloud_consent import ConsentGuardedProvider
    from personal_ai.core.openai_compatible import OpenAICompatibleProvider

    assert isinstance(provider, ConsentGuardedProvider)
    assert isinstance(provider._provider, OpenAICompatibleProvider)

def test_bootstrap_resolves_execution_strategy(monkeypatch, tmp_path):
    import personal_ai.application.bootstrap as bootstrap_module

    calls = []

    class SpyExecutionStrategyResolver:
        def __init__(self, provider_resolver):
            self.provider_resolver = provider_resolver

        def resolve(self, provider_id):
            calls.append(provider_id)
            return "fake"

    monkeypatch.setattr(
        bootstrap_module,
        "ExecutionStrategyResolver",
        SpyExecutionStrategyResolver,
        raising=False,
    )

    bootstrap(
        ApplicationPaths(
            config_dir=__import__("pathlib").Path("config"),
            data_dir=tmp_path / "data",
        )
    )

    assert calls == ["fake"]


def test_bootstrap_shares_tool_registry_and_executor_with_agent(tmp_path):
    from pathlib import Path

    from personal_ai.tools.executor import ToolExecutor
    from personal_ai.tools.registry import ToolRegistry

    application = bootstrap(
        ApplicationPaths(
            config_dir=Path("config"),
            data_dir=tmp_path / "data",
        )
    )

    assert isinstance(application.tool_registry, ToolRegistry)
    assert isinstance(application.tool_executor, ToolExecutor)
    assert application.agent.tool_registry is application.tool_registry
    assert application.agent.tool_executor is application.tool_executor
    assert application.tool_registry.tool_names == ("local_file_read",)


def test_bootstrap_registers_local_file_read_tool_without_granting_access(tmp_path):
    from pathlib import Path

    application = bootstrap(
        ApplicationPaths(
            config_dir=Path("config"),
            data_dir=tmp_path / "data",
        )
    )

    assert "local_file_read" in application.tool_registry.tool_names
    assert application.config.filesystem_scope.authorized_roots == ()
    assert (
        application.permission_evaluator.evaluate(
            "local_filesystem", "read"
        )
        == "denied"
    )

    result = application.agent.execute_registered_tool(
        name="local_file_read",
        input_data=str(tmp_path / "private.txt"),
        permission_evaluator=application.permission_evaluator,
    )

    assert result.status == "denied"
    assert result.result is None

def test_bootstrap_does_not_wrap_local_provider_in_consent_guard(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("PERSONAL_AI_LLM_PROVIDER", "fake")
    from personal_ai.core.cloud_consent import ConsentGuardedProvider

    application = bootstrap(
        ApplicationPaths(
            config_dir=__import__("pathlib").Path("config"),
            data_dir=tmp_path / "data",
        )
    )

    provider = application.agent.integration.runtime.provider
    assert not isinstance(provider, ConsentGuardedProvider)
