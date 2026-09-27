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

def test_executor_can_bind_additional_capabilities() -> None:
    executor = Executor({})

    bound = executor.with_capabilities(
        {
            "respond": lambda value: f"response: {value}",
        }
    )

    assert executor.capability_ids == ()
    assert bound.capability_ids == ("respond",)

    plan = ExecutionPlan(
        plan_id="plan-1",
        original_request="request",
        steps=(
            PlanStep("step-1", "respond", "hello"),
        ),
    )

    assert bound.execute(plan) == ["response: hello"]
def test_executor_rejects_duplicate_capability_binding() -> None:
    executor = Executor(
        {
            "respond": lambda value: value,
        }
    )

    with pytest.raises(ValueError, match="duplicate capability: respond"):
        executor.with_capabilities(
            {
                "respond": lambda value: f"replacement: {value}",
            }
        )

def test_executor_propagates_capability_failure() -> None:
    def failing_capability(value: object) -> object:
        raise RuntimeError("capability failed")

    executor = Executor({"failing": failing_capability})

    plan = ExecutionPlan(
        plan_id="plan-1",
        original_request="request",
        steps=(
            PlanStep("step-1", "failing", "input"),
        ),
    )

    with pytest.raises(RuntimeError, match="capability failed"):
        executor.execute(plan)
