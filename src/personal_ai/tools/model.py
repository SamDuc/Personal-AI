from dataclasses import dataclass


@dataclass
class ToolDefinition:
    name: str
    description: str
    resource_category: str
    operation: str
@dataclass
class ToolResult:
    status: str
    result: object | None = None
    error: str | None = None
