from pathlib import Path

from personal_ai.file_intelligence.authorization import AuthorizationGate
from personal_ai.file_intelligence.capability import resolve_file_capability
from personal_ai.filesystem.scope import FilesystemAccessScope
from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.permissions.policy import PermissionPolicy


def make_gate(
    tmp_path: Path,
    *,
    read: bool = True,
    confirmation_required: list[str] | None = None,
) -> AuthorizationGate:
    policy = PermissionPolicy(
        {
            "defaults": {
                "local_file": {
                    "read": read,
                    "write": False,
                }
            },
            "confirmation_required": confirmation_required or [],
        }
    )

    return AuthorizationGate(
        filesystem_scope=FilesystemAccessScope([tmp_path]),
        permission_evaluator=PermissionEvaluator(policy),
    )


def text_capability():
    return resolve_file_capability(
        mime_type="text/plain",
        extension=".txt",
    )


def pdf_capability():
    return resolve_file_capability(
        mime_type="application/pdf",
        extension=".pdf",
    )


def test_authorized_text_file_is_allowed(tmp_path: Path) -> None:
    path = tmp_path / "document.txt"
    path.write_text("hello", encoding="utf-8")

    decision = make_gate(tmp_path).evaluate(
        source_path=path,
        capability=text_capability(),
        resource_category="local_file",
    )

    assert decision.allowed is True
    assert decision.reason == "authorized"


def test_file_outside_scope_is_denied(tmp_path: Path) -> None:
    authorized = tmp_path / "authorized"
    outside = tmp_path / "outside"
    authorized.mkdir()
    outside.mkdir()

    path = outside / "document.txt"
    path.write_text("hello", encoding="utf-8")

    decision = make_gate(authorized).evaluate(
        source_path=path,
        capability=text_capability(),
        resource_category="local_file",
    )

    assert decision.allowed is False
    assert decision.reason == "filesystem_scope_denied"


def test_denied_read_permission_is_denied(tmp_path: Path) -> None:
    path = tmp_path / "document.txt"
    path.write_text("hello", encoding="utf-8")

    decision = make_gate(
        tmp_path,
        read=False,
    ).evaluate(
        source_path=path,
        capability=text_capability(),
        resource_category="local_file",
    )

    assert decision.allowed is False
    assert decision.reason == "permission_denied"


def test_confirmation_required_is_not_allowed(tmp_path: Path) -> None:
    path = tmp_path / "document.txt"
    path.write_text("hello", encoding="utf-8")

    decision = make_gate(
        tmp_path,
        confirmation_required=["read"],
    ).evaluate(
        source_path=path,
        capability=text_capability(),
        resource_category="local_file",
    )

    assert decision.allowed is False
    assert decision.reason == "permission_confirmation_required"


def test_unsupported_capability_is_denied(tmp_path: Path) -> None:
    path = tmp_path / "document.pdf"
    path.write_bytes(b"%PDF")

    decision = make_gate(tmp_path).evaluate(
        source_path=path,
        capability=pdf_capability(),
        resource_category="local_file",
    )

    assert decision.allowed is False
    assert decision.reason == "unsupported_capability"


def test_write_operation_is_not_granted(tmp_path: Path) -> None:
    path = tmp_path / "document.txt"
    path.write_text("hello", encoding="utf-8")

    decision = make_gate(tmp_path).evaluate(
        source_path=path,
        capability=text_capability(),
        resource_category="local_file",
        operation="write",
    )

    assert decision.allowed is False
    assert decision.reason == "permission_denied"


def test_unknown_resource_category_is_denied(tmp_path: Path) -> None:
    path = tmp_path / "document.txt"
    path.write_text("hello", encoding="utf-8")

    decision = make_gate(tmp_path).evaluate(
        source_path=path,
        capability=text_capability(),
        resource_category="unknown_resource",
    )

    assert decision.allowed is False
    assert decision.reason == "permission_denied"


def test_authorization_decision_is_immutable(tmp_path: Path) -> None:
    path = tmp_path / "document.txt"
    path.write_text("hello", encoding="utf-8")

    decision = make_gate(tmp_path).evaluate(
        source_path=path,
        capability=text_capability(),
        resource_category="local_file",
    )

    try:
        decision.allowed = False
    except AttributeError:
        pass
    else:
        raise AssertionError("AuthorizationDecision must be immutable")
