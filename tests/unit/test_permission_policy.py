from pathlib import Path

import pytest

from personal_ai.permissions.policy import PermissionPolicy

POLICY_PATH = Path("config/permissions/permissions.yaml")


def test_policy_loads_defaults() -> None:
    policy = PermissionPolicy.from_file(POLICY_PATH)

    defaults = policy.get_defaults()

    assert defaults["local_filesystem"]["read"] is False
    assert defaults["local_filesystem"]["write"] is False
    assert defaults["cloud_storage"]["read"] is False
    assert defaults["email"]["send"] is False
    assert defaults["database"]["write"] is False
    assert defaults["browser"]["interact"] is False


def test_policy_loads_confirmation_required_operations() -> None:
    policy = PermissionPolicy.from_file(POLICY_PATH)

    assert policy.get_confirmation_required() == [
        "move",
        "rename",
        "delete",
        "send",
        "share",
        "external_action",
    ]


def test_policy_returns_independent_defaults_copy() -> None:
    policy = PermissionPolicy.from_file(POLICY_PATH)

    first = policy.get_defaults()
    first["local_filesystem"]["read"] = True

    second = policy.get_defaults()

    assert second["local_filesystem"]["read"] is False


def test_policy_returns_independent_confirmation_list() -> None:
    policy = PermissionPolicy.from_file(POLICY_PATH)

    first = policy.get_confirmation_required()
    first.append("unexpected_operation")

    second = policy.get_confirmation_required()

    assert second == [
        "move",
        "rename",
        "delete",
        "send",
        "share",
        "external_action",
    ]


def test_policy_rejects_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        PermissionPolicy.from_file(
            "config/permissions/missing.yaml"
        )
def test_policy_does_not_alias_input_dictionary():
    policy_data = {
        "defaults": {
            "local_filesystem": {
                "read": False,
            },
        },
        "confirmation_required": [],
    }

    policy = PermissionPolicy(policy_data)

    policy_data["defaults"]["local_filesystem"]["read"] = True

    assert policy.get_defaults()["local_filesystem"]["read"] is False
