from personal_ai.tools.model import ToolDefinition
from personal_ai.tools.tool import Tool


class ToolRegistry:
    """Registry of explicitly registered tools."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    @property
    def tool_names(self) -> tuple[str, ...]:
        return tuple(self._tools)

    def register(self, tool: Tool) -> None:
        if not isinstance(tool, Tool):
            raise ValueError("tool must be a Tool instance")

        definition = getattr(tool, "definition", None)
        if not isinstance(definition, ToolDefinition):
            raise ValueError("tool must expose a valid ToolDefinition")

        name = definition.name
        if not isinstance(name, str) or not name.strip():
            raise ValueError("tool definition name must be non-empty")

        if name in self._tools:
            raise ValueError(f"tool already registered: {name}")

        self._tools[name] = tool

    def get(self, name: str) -> Tool | None:
        if not isinstance(name, str) or not name:
            raise ValueError("tool name must be a non-empty string")

        return self._tools.get(name)
