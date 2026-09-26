from dataclasses import dataclass


@dataclass
class ToolDefinition:
    name: str
    description: str
    resource_category: str
    operation: str
