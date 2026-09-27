from typing import Protocol

from personal_ai.core.planning import ExecutionPlan, PlanStep


class Planner(Protocol):
    def plan(self, user_request: str) -> ExecutionPlan: ...


class DeterministicPlanner:
    """Minimal deterministic planner.

    Planning produces data only. It does not execute capabilities.
    """

    def plan(self, user_request: str) -> ExecutionPlan:
        if not isinstance(user_request, str):
            raise ValueError("user_request must be a string")

        return ExecutionPlan(
            plan_id="deterministic-plan",
            original_request=user_request,
            steps=(
                PlanStep(
                    step_id="step-1",
                    capability="respond",
                    input_data=user_request,
                ),
            ),
        )
