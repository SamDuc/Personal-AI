from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.permissions.policy import PermissionPolicy
from personal_ai.tools.model import ToolResult
from personal_ai.tools.tool import Tool


def test_tool_executes_capability_only_when_permission_is_allowed():
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
    execution_count = 0

    class ProtectedTool(Tool):
        def execute(
            self,
            input_data: object,
            permission_evaluator: PermissionEvaluator,
        ) -> ToolResult:
            nonlocal execution_count

            decision = permission_evaluator.evaluate(
                resource_category="local_filesystem",
                operation="read",
            )

            if decision != "allowed":
                return ToolResult(status=decision)

            execution_count += 1
            return ToolResult(
                status="success",
                result=input_data,
            )

    tool = ProtectedTool()

    result = tool.execute(
        input_data="test",
        permission_evaluator=evaluator,
    )

    assert result.status == "success"
    assert result.result == "test"
    assert execution_count == 1
