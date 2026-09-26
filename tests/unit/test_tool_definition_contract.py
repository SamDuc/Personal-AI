from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.tools.model import ToolDefinition, ToolResult
from personal_ai.tools.tool import Tool


class FakeTool(Tool):
    definition = ToolDefinition(
        name="test_tool",
        description="Test tool",
        resource_category="local_filesystem",
        operation="read",
    )

    def execute(
        self,
        input_data: object,
        permission_evaluator: PermissionEvaluator,
    ) -> ToolResult:
        return ToolResult(
            status="success",
            result=input_data,
        )


def test_tool_exposes_definition():
    tool = FakeTool()

    assert isinstance(tool.definition, ToolDefinition)
    assert tool.definition.name == "test_tool"
    assert tool.definition.description == "Test tool"
    assert tool.definition.resource_category == "local_filesystem"
    assert tool.definition.operation == "read"
