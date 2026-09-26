from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.permissions.policy import PermissionPolicy
from personal_ai.tools.executor import ToolExecutor
from personal_ai.tools.model import ToolDefinition, ToolResult
from personal_ai.tools.tool import Tool


def make_evaluator(
    read: bool = False,
    confirmation_required: list[str] | None = None,
) -> PermissionEvaluator:
    policy = PermissionPolicy(
        {
            "defaults": {
                "local_filesystem": {
                    "read": read,
                },
            },
            "confirmation_required": confirmation_required or [],
        }
    )
    return PermissionEvaluator(policy)


class SpyTool(Tool):
    definition = ToolDefinition(
        name="spy_tool",
        description="Test tool for execution boundary.",
        resource_category="local_filesystem",
        operation="read",
    )

    def __init__(self) -> None:
        self.execution_count = 0

    def execute(
        self,
        input_data: object,
        permission_evaluator: PermissionEvaluator,
    ) -> ToolResult:
        self.execution_count += 1
        return ToolResult(status="success", result=input_data)


def test_executor_denied_does_not_execute_tool():
    tool = SpyTool()
    executor = ToolExecutor()
    evaluator = make_evaluator(read=False)

    result = executor.execute(tool, "secret", evaluator)

    assert result.status == "denied"
    assert result.result is None
    assert tool.execution_count == 0


def test_executor_confirmation_required_does_not_execute_tool():
    tool = SpyTool()
    executor = ToolExecutor()
    evaluator = make_evaluator(
        read=True,
        confirmation_required=["read"],
    )

    result = executor.execute(tool, "secret", evaluator)

    assert result.status == "confirmation_required"
    assert result.result is None
    assert tool.execution_count == 0


def test_executor_allowed_executes_tool():
    tool = SpyTool()
    executor = ToolExecutor()
    evaluator = make_evaluator(read=True)

    result = executor.execute(tool, "allowed", evaluator)

    assert result.status == "success"
    assert result.result == "allowed"
    assert tool.execution_count == 1
