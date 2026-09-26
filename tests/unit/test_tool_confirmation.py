from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.permissions.policy import PermissionPolicy
from personal_ai.tools.model import ToolResult
from personal_ai.tools.tool import Tool

POLICY_PATH = "config/permissions/permissions.yaml"


def test_tool_must_not_execute_when_confirmation_is_required():
    evaluator = PermissionEvaluator(
        PermissionPolicy.from_file(POLICY_PATH)
    )

    class ProtectedTool(Tool):
        def execute(
            self,
            input_data: object,
            permission_evaluator: PermissionEvaluator,
        ) -> ToolResult:
            decision = permission_evaluator.evaluate(
                resource_category="local_filesystem",
                operation="delete",
            )

            if decision == "confirmation_required":
                return ToolResult(status="confirmation_required")

            return ToolResult(status="success", result="executed")

    tool = ProtectedTool()

    result = tool.execute(
        input_data="test",
        permission_evaluator=evaluator,
    )

    assert result.status == "confirmation_required"
    assert result.result is None
