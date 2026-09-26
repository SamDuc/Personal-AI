from personal_ai.tools.model import ToolResult


def test_tool_result_success():
    result = ToolResult(
        status="success",
        result="file content",
    )

    assert result.status == "success"
    assert result.result == "file content"


def test_tool_result_permission_denied():
    result = ToolResult(
        status="permission_denied",
    )

    assert result.status == "permission_denied"
    assert result.result is None


def test_tool_result_confirmation_required():
    result = ToolResult(
        status="confirmation_required",
    )

    assert result.status == "confirmation_required"
    assert result.result is None


def test_tool_result_execution_failure():
    result = ToolResult(
        status="execution_failure",
        error="file could not be read",
    )

    assert result.status == "execution_failure"
    assert result.error == "file could not be read"


def test_tool_result_invalid_input():
    result = ToolResult(
        status="invalid_input",
        error="path is required",
    )

    assert result.status == "invalid_input"
    assert result.error == "path is required"
