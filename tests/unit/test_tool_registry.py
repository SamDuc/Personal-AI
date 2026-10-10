import pytest

from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.tools.local_file_read import LocalFileReadTool
from personal_ai.tools.model import ToolDefinition, ToolResult
from personal_ai.tools.registry import ToolRegistry
from personal_ai.tools.tool import Tool


class FakeTool(Tool):
    definition = ToolDefinition(
        name="fake",
        description="Test tool",
        resource_category="local_filesystem",
        operation="read",
    )

    def execute(
        self,
        input_data: object,
        permission_evaluator: PermissionEvaluator,
    ) -> ToolResult:
        return ToolResult(status="success", result=input_data)


def test_registry_registers_and_resolves_tool() -> None:
    registry = ToolRegistry()
    tool = FakeTool()

    registry.register(tool)

    assert registry.tool_names == ("fake",)
    assert registry.get("fake") is tool


def test_registry_returns_none_for_unknown_tool() -> None:
    registry = ToolRegistry()

    assert registry.get("missing") is None


def test_registry_rejects_duplicate_name_without_overwriting() -> None:
    registry = ToolRegistry()
    original = FakeTool()
    duplicate = FakeTool()

    registry.register(original)

    with pytest.raises(ValueError, match="already registered"):
        registry.register(duplicate)

    assert registry.get("fake") is original


def test_registry_rejects_non_tool_object() -> None:
    registry = ToolRegistry()

    with pytest.raises(ValueError, match="Tool instance"):
        registry.register(object())  # type: ignore[arg-type]


def test_registry_rejects_tool_without_definition() -> None:
    class MissingDefinitionTool(FakeTool):
        definition = None

    registry = ToolRegistry()

    with pytest.raises(ValueError, match="ToolDefinition"):
        registry.register(MissingDefinitionTool())


def test_registry_can_register_local_file_read_tool() -> None:
    registry = ToolRegistry()
    tool = LocalFileReadTool()

    registry.register(tool)

    assert registry.get("local_file_read") is tool
    assert registry.tool_names == ("local_file_read",)
