from pathlib import Path

from personal_ai.filesystem.scope import FilesystemAccessScope
from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.permissions.policy import PermissionPolicy
from personal_ai.tools.local_file_read import LocalFileReadTool


def make_evaluator(
    read: bool = False,
    confirmation_required: list[str] | None = None,
) -> PermissionEvaluator:
    policy = PermissionPolicy(
        {
            "defaults": {
                "local_filesystem": {
                    "read": read,
                },
            },
            "confirmation_required": confirmation_required or [],
        }
    )
    return PermissionEvaluator(policy)


def test_local_file_read_tool_metadata():
    tool = LocalFileReadTool()

    assert tool.definition.name == "local_file_read"
    assert tool.definition.resource_category == "local_filesystem"
    assert tool.definition.operation == "read"


def test_local_file_read_rejects_invalid_input():
    tool = LocalFileReadTool()
    evaluator = make_evaluator(read=True)

    result = tool.execute("", evaluator)

    assert result.status == "invalid_input"
    assert result.result is None
    assert result.error is not None


def test_local_file_read_does_not_execute_when_denied(tmp_path: Path):
    target = tmp_path / "secret.txt"
    target.write_text("secret", encoding="utf-8")

    tool = LocalFileReadTool()
    evaluator = make_evaluator(read=False)

    result = tool.execute(str(target), evaluator)

    assert result.status == "denied"
    assert result.result is None


def test_local_file_read_does_not_execute_when_confirmation_required(
    tmp_path: Path,
):
    target = tmp_path / "secret.txt"
    target.write_text("secret", encoding="utf-8")

    tool = LocalFileReadTool()
    evaluator = make_evaluator(
        read=True,
        confirmation_required=["read"],
    )

    result = tool.execute(str(target), evaluator)

    assert result.status == "confirmation_required"
    assert result.result is None


def test_local_file_read_denies_path_outside_scope(tmp_path: Path):
    target = tmp_path / "notes.txt"
    target.write_text("Personal AI local file.", encoding="utf-8")

    authorized_root = tmp_path / "authorized"
    authorized_root.mkdir()

    tool = LocalFileReadTool(
        filesystem_scope=FilesystemAccessScope([authorized_root]),
    )
    evaluator = make_evaluator(read=True)

    result = tool.execute(str(target), evaluator)

    assert result.status == "denied"
    assert result.result is None
    assert result.error is not None


def test_local_file_read_executes_when_allowed(tmp_path: Path):
    authorized_root = tmp_path / "authorized"
    authorized_root.mkdir()

    target = authorized_root / "notes.txt"
    target.write_text("Personal AI local file.", encoding="utf-8")

    tool = LocalFileReadTool(
        filesystem_scope=FilesystemAccessScope([authorized_root]),
    )
    evaluator = make_evaluator(read=True)

    result = tool.execute(str(target), evaluator)

    assert result.status == "success"
    assert result.result == "Personal AI local file."
    assert result.error is None


def test_local_file_read_reports_missing_file(tmp_path: Path):
    authorized_root = tmp_path / "authorized"
    authorized_root.mkdir()

    target = authorized_root / "missing.txt"

    tool = LocalFileReadTool(
        filesystem_scope=FilesystemAccessScope([authorized_root]),
    )
    evaluator = make_evaluator(read=True)

    result = tool.execute(str(target), evaluator)

    assert result.status == "execution_failure"
    assert result.result is None
    assert result.error is not None


def test_local_file_read_rejects_directory(tmp_path: Path):
    authorized_root = tmp_path / "authorized"
    authorized_root.mkdir()

    tool = LocalFileReadTool(
        filesystem_scope=FilesystemAccessScope([authorized_root]),
    )
    evaluator = make_evaluator(read=True)

    result = tool.execute(str(authorized_root), evaluator)

    assert result.status == "invalid_input"
    assert result.result is None
    assert result.error is not None
