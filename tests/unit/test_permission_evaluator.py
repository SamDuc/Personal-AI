from pathlib import Path

import pytest

from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.permissions.policy import PermissionPolicy

POLICY_PATH = Path("config/permissions/permissions.yaml")


@pytest.fixture
def evaluator() -> PermissionEvaluator:
    policy = PermissionPolicy.from_file(POLICY_PATH)
    return PermissionEvaluator(policy)


def test_denies_operation_when_policy_disallows_it(
    evaluator: PermissionEvaluator,
) -> None:
    decision = evaluator.evaluate(
        resource_category="local_filesystem",
        operation="read",
    )

    assert decision == "denied"


def test_denies_unknown_resource_category(
    evaluator: PermissionEvaluator,
) -> None:
    decision = evaluator.evaluate(
        resource_category="unknown_resource",
        operation="read",
    )

    assert decision == "denied"


def test_denies_unknown_operation(
    evaluator: PermissionEvaluator,
) -> None:
    decision = evaluator.evaluate(
        resource_category="local_filesystem",
        operation="unknown_operation",
    )

    assert decision == "denied"


def test_requires_confirmation_for_confirmation_operation(
    evaluator: PermissionEvaluator,
) -> None:
    decision = evaluator.evaluate(
        resource_category="local_filesystem",
        operation="delete",
    )

    assert decision == "confirmation_required"


def test_confirmation_operation_is_not_authorized(
    evaluator: PermissionEvaluator,
) -> None:
    decision = evaluator.evaluate(
        resource_category="email",
        operation="send",
    )

    assert decision != "allowed"