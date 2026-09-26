from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.permissions.policy import PermissionPolicy
from personal_ai.tools.model import ToolResult
from personal_ai.tools.tool import Tool

POLICY_PATH = "config/permissions/permissions.yaml"


def test_tool_is_replaceable_interface():
    evaluator = PermissionEvaluator(
        PermissionPolicy.from_file(POLICY_PATH)
    )

    class FakeTool(Tool):
        def execute(
            self,
            input_data: object,
            permission_evaluator: PermissionEvaluator,
        ) -> ToolResult:
            return ToolResult(
                status="success",
                result=input_data,
            )

    tool = FakeTool()

    result = tool.execute(
        input_data="test",
        permission_evaluator=evaluator,
    )

    assert result.status == "success"
    assert result.result == "test"
