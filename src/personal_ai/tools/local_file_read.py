from pathlib import Path

from personal_ai.filesystem.scope import FilesystemAccessScope
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

    def __init__(
        self,
        filesystem_scope: FilesystemAccessScope | None = None,
    ) -> None:
        self.filesystem_scope = filesystem_scope or FilesystemAccessScope([])

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

        resolved_path = self.filesystem_scope.resolve_allowed_path(path)
        if resolved_path is None:
            return ToolResult(
                status="denied",
                error=f"Path is outside authorized filesystem scope: {path}",
            )

        if not resolved_path.exists():
            return ToolResult(
                status="execution_failure",
                error=f"File does not exist: {path}",
            )

        if not resolved_path.is_file():
            return ToolResult(
                status="invalid_input",
                error=f"Path is not a file: {path}",
            )

        max_file_bytes = 1024 * 1024

        try:
            with resolved_path.open("rb") as file_handle:
                raw_content = file_handle.read(max_file_bytes + 1)

            if len(raw_content) > max_file_bytes:
                return ToolResult(
                    status="invalid_input",
                    error="File exceeds the 1 MiB read limit.",
                )

            content = raw_content.decode("utf-8")
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
