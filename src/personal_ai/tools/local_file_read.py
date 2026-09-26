from pathlib import Path

from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.tools.model import ToolDefinition, ToolResult
from personal_ai.tools.tool import Tool


class LocalFileReadTool(Tool):
    definition = ToolDefinition(
        name="local_file_read",
        description="Read the text content of an authorized local file.",
        resource_category="local_filesystem",
        operation="read",
    )

    def execute(
        self,
        input_data: object,
        permission_evaluator: PermissionEvaluator,
    ) -> ToolResult:
        if not isinstance(input_data, str) or not input_data.strip():
            return ToolResult(
                status="invalid_input",
                error="input_data must be a non-empty file path string",
            )

        path = Path(input_data)

        decision = permission_evaluator.evaluate(
            resource_category=self.definition.resource_category,
            operation=self.definition.operation,
        )

        if decision != "allowed":
            return ToolResult(status=decision)

        if not path.exists():
            return ToolResult(
                status="execution_failure",
                error=f"File does not exist: {path}",
            )

        if not path.is_file():
            return ToolResult(
                status="invalid_input",
                error=f"Path is not a file: {path}",
            )

        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            return ToolResult(
                status="execution_failure",
                error=str(exc),
            )
        except UnicodeDecodeError as exc:
            return ToolResult(
                status="execution_failure",
                error=f"File is not valid UTF-8 text: {exc}",
            )

        return ToolResult(
            status="success",
            result=content,
        )
