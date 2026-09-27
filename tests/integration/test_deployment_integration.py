from pathlib import Path

from personal_ai.application.bootstrap import bootstrap
from personal_ai.application.paths import ApplicationPaths
from personal_ai.core.conversation_session import ConversationSession


def test_deployment_boundary_supports_safe_operation(tmp_path):
    paths = ApplicationPaths(
        config_dir=Path("config"),
        data_dir=tmp_path / "data",
    )

    application = bootstrap(paths)

    assert application.config.llm_config.providers["fake"]["enabled"] is True
    assert application.permission_evaluator.evaluate(
        "local_filesystem", "read"
    ) == "denied"

    session = ConversationSession()
    result = application.agent.run("Run a safe deployment smoke test.", session)

    assert result == "fake response"
    assert session.messages[-1].role == "assistant"
    assert session.messages[-1].content == "fake response"
    assert not (tmp_path / "data").exists()
