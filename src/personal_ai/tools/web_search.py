from __future__ import annotations

from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.tools.model import ToolDefinition, ToolResult
from personal_ai.tools.search_providers import DisabledSearchProvider, SearchProvider
from personal_ai.tools.tool import Tool


class WebSearchTool(Tool):
    definition = ToolDefinition(
        name="web_search",
        description="Search public websites and return titles/URLs; use web_fetch to read a result.",
        resource_category="browser",
        operation="read",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The web search query."}
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    )

    def __init__(
        self,
        provider: SearchProvider | None = None,
        *,
        max_results: int = 5,
    ) -> None:
        if (
            isinstance(max_results, bool)
            or not isinstance(max_results, int)
            or not 1 <= max_results <= 10
        ):
            raise ValueError("max_results must be an integer from 1 to 10.")
        self._provider = provider or DisabledSearchProvider()
        self._max_results = max_results

    def execute(
        self,
        input_data: object,
        permission_evaluator: PermissionEvaluator,
    ) -> ToolResult:
        decision = permission_evaluator.evaluate(
            resource_category=self.definition.resource_category,
            operation=self.definition.operation,
        )
        if decision != "allowed":
            return ToolResult(status=decision, error="Web access permission is not granted.")
        if not isinstance(input_data, dict):
            return ToolResult(status="invalid_input", error="Expected an object containing query.")
        query = input_data.get("query")
        if not isinstance(query, str) or not query.strip():
            return ToolResult(status="invalid_input", error="query must be a non-empty string.")
        query = query.strip()
        if len(query) > 500:
            return ToolResult(status="invalid_input", error="query is too long.")

        try:
            results = self._provider.search(query, self._max_results)
        except (RuntimeError, ValueError) as exc:
            return ToolResult(status="execution_failure", error=str(exc))

        if not isinstance(results, list) or not results:
            return ToolResult(
                status="execution_failure",
                error="Search provider returned no usable results.",
            )
        normalized: list[dict[str, str]] = []
        for item in results[: self._max_results]:
            if (
                not isinstance(item, dict)
                or not isinstance(item.get("title"), str)
                or not isinstance(item.get("url"), str)
            ):
                return ToolResult(
                    status="execution_failure",
                    error="Search provider returned a result with an invalid schema.",
                )
            normalized.append({"title": item["title"], "url": item["url"]})

        return ToolResult(
            status="success",
            result={"query": query, "results": normalized},
        )
