from personal_ai.tools.model import ToolDefinition


def test_tool_definition_fields():
    tool = ToolDefinition(
        name="read_local_file",
        description="Read a local file",
        resource_category="local_filesystem",
        operation="read",
    )

    assert tool.name == "read_local_file"
    assert tool.description == "Read a local file"
    assert tool.resource_category == "local_filesystem"
    assert tool.operation == "read"
