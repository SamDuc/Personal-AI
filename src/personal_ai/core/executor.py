from collections.abc import Callable

from personal_ai.core.planning import ExecutionPlan

Capability = Callable[[object], object]


class Executor:
    def __init__(self, capabilities: dict[str, Capability]) -> None:
        if not isinstance(capabilities, dict):
            raise ValueError("capabilities must be a dictionary")
        self._capabilities = dict(capabilities)

    @property
    def capability_ids(self) -> tuple[str, ...]:
        return tuple(self._capabilities)

    def execute(self, plan: ExecutionPlan) -> list[object]:
        if not isinstance(plan, ExecutionPlan):
            raise ValueError("plan must be an ExecutionPlan")

        results: list[object] = []

        for step in plan.steps:
            capability = self._capabilities.get(step.capability)
            if capability is None:
                raise ValueError(f"unknown capability: {step.capability}")

            results.append(capability(step.input_data))

        return results
