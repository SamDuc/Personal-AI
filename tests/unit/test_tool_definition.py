from personal_ai.tools.model import ToolDefinition


def test_tool_definition_declares_permission_scope():
    definition = ToolDefinition(
        name="test_tool",
        description="Test tool",
        resource_category="local_filesystem",
        operation="read",
    )

    assert definition.name == "test_tool"
    assert definition.description == "Test tool"
    assert definition.resource_category == "local_filesystem"
    assert definition.operation == "read"
