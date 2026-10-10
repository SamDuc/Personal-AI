from pathlib import Path

from personal_ai.core.agent import Agent
from personal_ai.filesystem.scope import FilesystemAccessScope
from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.permissions.policy import PermissionPolicy
from personal_ai.tools.executor import ToolExecutor
from personal_ai.tools.local_file_read import LocalFileReadTool


def test_agent_executes_registered_tool_when_allowed(tmp_path: Path):
    target = tmp_path / "registered.txt"
    target.write_text("Registered tool works.", encoding="utf-8")

    tool = LocalFileReadTool(
        filesystem_scope=FilesystemAccessScope([tmp_path]),
    )
    from personal_ai.tools.registry import ToolRegistry

    registry = ToolRegistry()
    registry.register(tool)
    agent = Agent(
        integration=None,  # type: ignore[arg-type]
        tool_registry=registry,
    )

    result = agent.execute_registered_tool(
        name="local_file_read",
        input_data=str(target),
        permission_evaluator=make_evaluator(read=True),
    )

    assert result.status == "success"
    assert result.result == "Registered tool works."


def test_agent_rejects_unregistered_tool():
    import pytest

    from personal_ai.tools.registry import ToolRegistry

    agent = Agent(
        integration=None,  # type: ignore[arg-type]
        tool_registry=ToolRegistry(),
    )

    with pytest.raises(ValueError, match="tool is not registered"):
        agent.execute_registered_tool(
            name="missing",
            input_data="unused",
            permission_evaluator=make_evaluator(read=True),
        )


def test_agent_does_not_execute_registered_tool_when_denied(
    tmp_path: Path,
):
    target = tmp_path / "denied.txt"
    target.write_text("Must not be returned.", encoding="utf-8")

    tool = LocalFileReadTool(
        filesystem_scope=FilesystemAccessScope([tmp_path]),
    )
    from personal_ai.tools.registry import ToolRegistry

    registry = ToolRegistry()
    registry.register(tool)
    agent = Agent(
        integration=None,  # type: ignore[arg-type]
        tool_registry=registry,
    )

    result = agent.execute_registered_tool(
        name="local_file_read",
        input_data=str(target),
        permission_evaluator=make_evaluator(read=False),
    )

    assert result.status == "denied"
    assert result.result is None


def make_evaluator(read: bool) -> PermissionEvaluator:
    return PermissionEvaluator(
        PermissionPolicy(
            {
                "defaults": {
                    "local_filesystem": {
                        "read": read,
                    },
                },
                "confirmation_required": [],
            }
        )
    )


def test_agent_can_coordinate_explicit_tool_execution(tmp_path: Path):
    target = tmp_path / "agent.txt"
    target.write_text(
        "Agent coordinated a local file read.",
        encoding="utf-8",
    )

    tool = LocalFileReadTool(
        filesystem_scope=FilesystemAccessScope([tmp_path]),
    )
    executor = ToolExecutor()
    evaluator = make_evaluator(read=True)

    agent = Agent(
        integration=None,  # type: ignore[arg-type]
    )

    result = agent.execute_tool(
        tool=tool,
        executor=executor,
        input_data=str(target),
        permission_evaluator=evaluator,
    )

    assert result.status == "success"
    assert result.result == "Agent coordinated a local file read."


def test_agent_tool_coordination_preserves_permission_boundary(
    tmp_path: Path,
):
    target = tmp_path / "protected.txt"
    target.write_text(
        "Protected content.",
        encoding="utf-8",
    )

    tool = LocalFileReadTool(
        filesystem_scope=FilesystemAccessScope([tmp_path]),
    )
    executor = ToolExecutor()
    evaluator = make_evaluator(read=False)

    agent = Agent(
        integration=None,  # type: ignore[arg-type]
    )

    result = agent.execute_tool(
        tool=tool,
        executor=executor,
        input_data=str(target),
        permission_evaluator=evaluator,
    )

    assert result.status == "denied"
    assert result.result is None


def test_agent_tool_coordination_does_not_read_files_directly():
    agent = Agent(
        integration=None,  # type: ignore[arg-type]
    )

    assert not hasattr(agent, "read_file")
    assert not hasattr(agent, "search_local_content")
