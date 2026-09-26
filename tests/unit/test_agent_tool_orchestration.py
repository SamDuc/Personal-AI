from pathlib import Path

from personal_ai.core.agent import Agent
from personal_ai.filesystem.scope import FilesystemAccessScope
from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.permissions.policy import PermissionPolicy
from personal_ai.tools.executor import ToolExecutor
from personal_ai.tools.local_file_read import LocalFileReadTool


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
