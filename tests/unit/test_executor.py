import pytest

from personal_ai.core.executor import Executor
from personal_ai.core.planning import ExecutionPlan, PlanStep


def test_executor_runs_steps_in_order() -> None:
    calls: list[str] = []

    def first(value: object) -> object:
        calls.append("first")
        return value

    def second(value: object) -> object:
        calls.append("second")
        return value

    executor = Executor(
        {
            "first": first,
            "second": second,
        }
    )

    plan = ExecutionPlan(
        plan_id="plan-1",
        original_request="request",
        steps=(
            PlanStep("step-1", "first", "a"),
            PlanStep("step-2", "second", "b"),
        ),
    )

    results = executor.execute(plan)

    assert calls == ["first", "second"]
    assert results == ["a", "b"]


def test_executor_rejects_unknown_capability() -> None:
    executor = Executor({})

    plan = ExecutionPlan(
        plan_id="plan-1",
        original_request="request",
        steps=(
            PlanStep("step-1", "missing"),
        ),
    )

    with pytest.raises(ValueError, match="unknown capability"):
        executor.execute(plan)


def test_executor_rejects_invalid_plan() -> None:
    executor = Executor({})

    with pytest.raises(ValueError, match="ExecutionPlan"):
        executor.execute("not-a-plan")
