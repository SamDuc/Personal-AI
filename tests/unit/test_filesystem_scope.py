from pathlib import Path

import pytest

from personal_ai.filesystem.scope import FilesystemAccessScope


def test_path_inside_authorized_root_is_allowed(tmp_path: Path) -> None:
    root = tmp_path / "allowed"
    root.mkdir()
    target = root / "notes.txt"
    target.write_text("test", encoding="utf-8")

    scope = FilesystemAccessScope([root])

    assert scope.is_allowed(target) is True


def test_path_outside_authorized_root_is_denied(tmp_path: Path) -> None:
    root = tmp_path / "allowed"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()

    scope = FilesystemAccessScope([root])

    assert scope.is_allowed(outside / "secret.txt") is False


def test_empty_scope_denies_all_paths(tmp_path: Path) -> None:
    scope = FilesystemAccessScope([])

    assert scope.is_allowed(tmp_path / "file.txt") is False


def test_sibling_prefix_is_not_authorized(tmp_path: Path) -> None:
    root = tmp_path / "allowed"
    sibling = tmp_path / "allowed-secret"
    root.mkdir()
    sibling.mkdir()

    scope = FilesystemAccessScope([root])

    assert scope.is_allowed(sibling / "secret.txt") is False


def test_parent_traversal_cannot_escape_scope(tmp_path: Path) -> None:
    root = tmp_path / "allowed"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()

    scope = FilesystemAccessScope([root])
    traversal = root / ".." / "outside" / "secret.txt"

    assert scope.is_allowed(traversal) is False


def test_nested_path_is_allowed(tmp_path: Path) -> None:
    root = tmp_path / "allowed"
    nested = root / "nested" / "deep"
    nested.mkdir(parents=True)

    scope = FilesystemAccessScope([root])

    assert scope.is_allowed(nested / "file.txt") is True


def test_relative_path_is_resolved_against_current_working_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "allowed"
    root.mkdir()

    monkeypatch.chdir(tmp_path)
    scope = FilesystemAccessScope(["allowed"])

    assert scope.is_allowed(Path("allowed") / "file.txt") is True


def test_symlink_is_evaluated_using_resolved_path(tmp_path: Path) -> None:
    root = tmp_path / "allowed"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()

    target = outside / "secret.txt"
    target.write_text("secret", encoding="utf-8")

    link = root / "link.txt"
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("Symlink creation is unavailable on this system.")

    scope = FilesystemAccessScope([root])

    assert scope.is_allowed(link) is False
