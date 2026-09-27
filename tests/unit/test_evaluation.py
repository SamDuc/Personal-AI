import pytest

from personal_ai.core.evaluation import (
    SUPPORTED_EVALUATION_VERSION,
    EvaluationContract,
    EvaluationEvidence,
    EvaluationResult,
)
from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.permissions.policy import PermissionPolicy


def test_evaluation_passes_without_failures() -> None:
    result = EvaluationContract().evaluate(
        evaluation_id="security-check",
        checks=("permission-deny-by-default", "filesystem-scope"),
    )

    assert isinstance(result, EvaluationResult)
    assert result.passed is True
    assert result.checks == (
        "permission-deny-by-default",
        "filesystem-scope",
    )
    assert result.failures == ()
    assert result.evidence == ()
    assert result.version == SUPPORTED_EVALUATION_VERSION


def test_evaluation_fails_with_explicit_failure() -> None:
    result = EvaluationContract().evaluate(
        evaluation_id="security-check",
        checks=("permission-deny-by-default",),
        failures=("permission invariant failed",),
    )

    assert result.passed is False
    assert result.failures == ("permission invariant failed",)


def test_evaluation_preserves_supplied_evidence() -> None:
    evidence = EvaluationEvidence(
        evidence_id="evidence-1",
        evaluation_id="security-check",
        check="permission-deny-by-default",
        passed=True,
        detail="read operation remained denied",
    )

    result = EvaluationContract().evaluate(
        evaluation_id="security-check",
        checks=("permission-deny-by-default",),
        evidence=(evidence,),
    )

    assert result.passed is True
    assert result.evidence == (evidence,)


def test_evaluation_rejects_evidence_from_another_evaluation() -> None:
    evidence = EvaluationEvidence(
        evidence_id="evidence-1",
        evaluation_id="other-check",
        check="permission-deny-by-default",
        passed=True,
        detail="read operation remained denied",
    )

    with pytest.raises(ValueError, match="evidence evaluation_id"):
        EvaluationContract().evaluate(
            evaluation_id="security-check",
            checks=("permission-deny-by-default",),
            evidence=(evidence,),
        )


def test_evaluation_rejects_evidence_for_unknown_check() -> None:
    evidence = EvaluationEvidence(
        evidence_id="evidence-1",
        evaluation_id="security-check",
        check="filesystem-scope",
        passed=True,
        detail="filesystem remained scoped",
    )

    with pytest.raises(ValueError, match="evidence check"):
        EvaluationContract().evaluate(
            evaluation_id="security-check",
            checks=("permission-deny-by-default",),
            evidence=(evidence,),
        )


def test_evaluation_requires_identifier() -> None:
    with pytest.raises(ValueError, match="evaluation_id"):
        EvaluationContract().evaluate(
            evaluation_id="",
            checks=(),
        )


def test_evaluation_requires_tuple_checks() -> None:
    with pytest.raises(ValueError, match="checks"):
        EvaluationContract().evaluate(
            evaluation_id="check",
            checks=["permission"],
        )


def test_evaluation_rejects_empty_check_name() -> None:
    with pytest.raises(ValueError, match="checks"):
        EvaluationContract().evaluate(
            evaluation_id="check",
            checks=("",),
        )


def test_evaluation_rejects_empty_failure_name() -> None:
    with pytest.raises(ValueError, match="failures"):
        EvaluationContract().evaluate(
            evaluation_id="check",
            checks=("permission",),
            failures=("",),
        )


def test_evaluation_rejects_unsupported_version() -> None:
    with pytest.raises(ValueError, match="unsupported evaluation version"):
        EvaluationResult(
            evaluation_id="check",
            passed=True,
            checks=(),
            failures=(),
            version=99,
        )


def test_evaluation_result_is_immutable() -> None:
    result = EvaluationContract().evaluate(
        evaluation_id="check",
        checks=("permission",),
    )

    with pytest.raises(AttributeError):
        result.passed = False


def test_evaluation_evidence_is_immutable() -> None:
    evidence = EvaluationEvidence(
        evidence_id="evidence-1",
        evaluation_id="check",
        check="permission",
        passed=True,
        detail="permission remained denied",
    )

    with pytest.raises(AttributeError):
        evidence.passed = False


def test_passing_evaluation_does_not_grant_permission() -> None:
    policy = PermissionPolicy(
        {
            "defaults": {
                "local_filesystem": {
                    "read": False,
                },
            },
            "confirmation_required": [],
        }
    )
    evaluator = PermissionEvaluator(policy)

    before = evaluator.evaluate(
        resource_category="local_filesystem",
        operation="read",
    )

    result = EvaluationContract().evaluate(
        evaluation_id="security-check",
        checks=("permission-deny-by-default",),
        evidence=(
            EvaluationEvidence(
                evidence_id="evidence-1",
                evaluation_id="security-check",
                check="permission-deny-by-default",
                passed=True,
                detail="read operation remained denied",
            ),
        ),
    )

    after = evaluator.evaluate(
        resource_category="local_filesystem",
        operation="read",
    )

    assert result.passed is True
    assert before == "denied"
    assert after == "denied"