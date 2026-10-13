from __future__ import annotations

from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.tools.model import ToolDefinition, ToolResult
from personal_ai.tools.tool import Tool
from personal_ai.tools.web_common import VisibleTextParser, fetch_bytes


class WebFetchTool(Tool):
    definition = ToolDefinition(
        name="web_fetch",
        description="Read visible text from a public HTTPS webpage; scripts are not executed.",
        resource_category="browser",
        operation="read",
        parameters={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Public HTTPS webpage URL."}
            },
            "required": ["url"],
            "additionalProperties": False,
        },
    )

    def execute(self, input_data: object, permission_evaluator: PermissionEvaluator) -> ToolResult:
        decision = permission_evaluator.evaluate(
            resource_category=self.definition.resource_category,
            operation=self.definition.operation,
        )
        if decision != "allowed":
            return ToolResult(status=decision, error="Web access permission is not granted.")
        if not isinstance(input_data, dict):
            return ToolResult(status="invalid_input", error="Expected an object containing url.")
        url = input_data.get("url")
        if not isinstance(url, str) or not url.strip():
            return ToolResult(status="invalid_input", error="url must be a non-empty string.")
        try:
            final_url, content_type, body = fetch_bytes(url)
            content = body.decode("utf-8", errors="replace")
            if content_type in ("text/html", "application/xhtml+xml"):
                parser = VisibleTextParser()
                parser.feed(content)
                content = parser.text()
            return ToolResult(status="success", result={"url": final_url, "text": content[:20000]})
        except (ValueError, RuntimeError) as exc:
            return ToolResult(status="execution_failure", error=str(exc))
