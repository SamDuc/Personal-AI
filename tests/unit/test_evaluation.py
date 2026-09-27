import pytest

from personal_ai.core.evaluation import (
    SUPPORTED_EVALUATION_VERSION,
    EvaluationContract,
    EvaluationResult,
)


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
    assert result.version == SUPPORTED_EVALUATION_VERSION


def test_evaluation_fails_with_explicit_failure() -> None:
    result = EvaluationContract().evaluate(
        evaluation_id="security-check",
        checks=("permission-deny-by-default",),
        failures=("permission invariant failed",),
    )

    assert result.passed is False
    assert result.failures == ("permission invariant failed",)


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
