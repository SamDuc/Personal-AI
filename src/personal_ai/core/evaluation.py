from dataclasses import dataclass
from typing import Final

SUPPORTED_EVALUATION_VERSION: Final = 1


@dataclass(frozen=True)
class EvaluationResult:
    """Immutable result of evaluating an application operation."""

    evaluation_id: str
    passed: bool
    checks: tuple[str, ...]
    failures: tuple[str, ...]
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

        if self.version != SUPPORTED_EVALUATION_VERSION:
            raise ValueError("unsupported evaluation version")


class EvaluationContract:
    """Deterministic evaluator for explicit security/application checks."""

    def evaluate(
        self,
        evaluation_id: str,
        checks: tuple[str, ...],
        failures: tuple[str, ...] = (),
    ) -> EvaluationResult:
        if not isinstance(evaluation_id, str) or not evaluation_id:
            raise ValueError("evaluation_id must be a non-empty string")

        if not isinstance(checks, tuple):
            raise ValueError("checks must be a tuple")

        if not isinstance(failures, tuple):
            raise ValueError("failures must be a tuple")

        if any(not isinstance(check, str) or not check for check in checks):
            raise ValueError("checks must contain non-empty strings")

        if any(not isinstance(failure, str) or not failure for failure in failures):
            raise ValueError("failures must contain non-empty strings")

        return EvaluationResult(
            evaluation_id=evaluation_id,
            passed=len(failures) == 0,
            checks=checks,
            failures=failures,
        )
