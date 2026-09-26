from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.permissions.policy import PermissionPolicy
from personal_ai.tools.model import ToolResult
from personal_ai.tools.tool import Tool


def test_tool_executes_when_permission_is_allowed():
    policy = PermissionPolicy(
        {
            "defaults": {
                "local_filesystem": {
                    "read": True,
                },
            },
            "confirmation_required": [],
        }
    )

    evaluator = PermissionEvaluator(policy)

    class ProtectedTool(Tool):
        def execute(
            self,
            input_data: object,
            permission_evaluator: PermissionEvaluator,
        ) -> ToolResult:
            decision = permission_evaluator.evaluate(
                resource_category="local_filesystem",
                operation="read",
            )

            if decision == "allowed":
                return ToolResult(
                    status="success",
                    result=input_data,
                )

            return ToolResult(status=decision)

    tool = ProtectedTool()

    result = tool.execute(
        input_data="test",
        permission_evaluator=evaluator,
    )

    assert result.status == "success"
    assert result.result == "test"
