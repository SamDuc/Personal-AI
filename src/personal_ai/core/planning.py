from dataclasses import dataclass
from typing import Final

SUPPORTED_PLAN_VERSION: Final = 1


@dataclass(frozen=True)
class PlanStep:
    step_id: str
    capability: str
    input_data: object = None

    def __post_init__(self) -> None:
        if not isinstance(self.step_id, str) or not self.step_id:
            raise ValueError("step_id must be a non-empty string")

        if not isinstance(self.capability, str) or not self.capability:
            raise ValueError("capability must be a non-empty string")


@dataclass(frozen=True)
class ExecutionPlan:
    plan_id: str
    original_request: str
    steps: tuple[PlanStep, ...]
    version: int = SUPPORTED_PLAN_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.plan_id, str) or not self.plan_id:
            raise ValueError("plan_id must be a non-empty string")

        if not isinstance(self.original_request, str):
            raise ValueError("original_request must be a string")

        if self.version != SUPPORTED_PLAN_VERSION:
            raise ValueError("unsupported plan version")

        if not isinstance(self.steps, tuple):
            raise ValueError("steps must be a tuple")

        step_ids = [step.step_id for step in self.steps]

        if len(step_ids) != len(set(step_ids)):
            raise ValueError("duplicate step_id")
