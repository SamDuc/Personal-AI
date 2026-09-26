from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.tools.model import ToolResult
from personal_ai.tools.tool import Tool


class ToolExecutor:
    def execute(
        self,
        tool: Tool,
        input_data: object,
        permission_evaluator: PermissionEvaluator,
    ) -> ToolResult:
        decision = permission_evaluator.evaluate(
            resource_category=tool.definition.resource_category,
            operation=tool.definition.operation,
        )

        if decision != "allowed":
            return ToolResult(status=decision)

        return tool.execute(
            input_data=input_data,
            permission_evaluator=permission_evaluator,
        )
