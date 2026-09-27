from dataclasses import dataclass
from typing import Final

SUPPORTED_EVALUATION_VERSION: Final = 1


@dataclass(frozen=True)
class EvaluationEvidence:
    """Immutable evidence supplied to an evaluation."""

    evidence_id: str
    evaluation_id: str
    check: str
    passed: bool
    detail: str
    version: int = SUPPORTED_EVALUATION_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.evidence_id, str) or not self.evidence_id:
            raise ValueError("evidence_id must be a non-empty string")

        if not isinstance(self.evaluation_id, str) or not self.evaluation_id:
            raise ValueError("evaluation_id must be a non-empty string")

        if not isinstance(self.check, str) or not self.check:
            raise ValueError("check must be a non-empty string")

        if not isinstance(self.passed, bool):
            raise ValueError("passed must be a boolean")

        if not isinstance(self.detail, str):
            raise ValueError("detail must be a string")

        if self.version != SUPPORTED_EVALUATION_VERSION:
            raise ValueError("unsupported evaluation version")


@dataclass(frozen=True)
class EvaluationResult:
    """Immutable result of evaluating an application operation."""

    evaluation_id: str
    passed: bool
    checks: tuple[str, ...]
    failures: tuple[str, ...]
    evidence: tuple[EvaluationEvidence, ...] = ()
    version: int = SUPPORTED_EVALUATION_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.evaluation_id, str) or not self.evaluation_id:
            raise ValueError("evaluation_id must be a non-empty string")

        if not isinstance(self.passed, bool):
            raise ValueError("passed must be a boolean")

        if not isinstance(self.checks, tuple):
            raise ValueError("checks must be a tuple")

        if not isinstance(self.failures, tuple):
            raise ValueError("failures must be a tuple")

        if not isinstance(self.evidence, tuple):
            raise ValueError("evidence must be a tuple")

        if any(not isinstance(item, EvaluationEvidence) for item in self.evidence):
            raise ValueError("evidence must contain EvaluationEvidence items")

        if any(item.evaluation_id != self.evaluation_id for item in self.evidence):
            raise ValueError("evidence evaluation_id must match evaluation_id")

        if any(item.check not in self.checks for item in self.evidence):
            raise ValueError("evidence check must be present in checks")

        if self.version != SUPPORTED_EVALUATION_VERSION:
            raise ValueError("unsupported evaluation version")


class EvaluationContract:
    """Deterministic evaluator for explicit security/application checks."""

    def evaluate(
        self,
        evaluation_id: str,
        checks: tuple[str, ...],
        failures: tuple[str, ...] = (),
        evidence: tuple[EvaluationEvidence, ...] = (),
    ) -> EvaluationResult:
        if not isinstance(evaluation_id, str) or not evaluation_id:
            raise ValueError("evaluation_id must be a non-empty string")

        if not isinstance(checks, tuple):
            raise ValueError("checks must be a tuple")

        if not isinstance(failures, tuple):
            raise ValueError("failures must be a tuple")

        if not isinstance(evidence, tuple):
            raise ValueError("evidence must be a tuple")

        if any(not isinstance(check, str) or not check for check in checks):
            raise ValueError("checks must contain non-empty strings")

        if any(not isinstance(failure, str) or not failure for failure in failures):
            raise ValueError("failures must contain non-empty strings")

        if any(not isinstance(item, EvaluationEvidence) for item in evidence):
            raise ValueError("evidence must contain EvaluationEvidence items")

        return EvaluationResult(
            evaluation_id=evaluation_id,
            passed=len(failures) == 0,
            checks=checks,
            failures=failures,
            evidence=evidence,
        )