import pytest

from personal_ai.core.planner import DeterministicPlanner
from personal_ai.core.planning import ExecutionPlan


def test_deterministic_planner_preserves_request() -> None:
    planner = DeterministicPlanner()

    plan = planner.plan("Find my project notes.")

    assert plan.original_request == "Find my project notes."
    assert len(plan.steps) == 1
    assert plan.steps[0].capability == "respond"
    assert plan.steps[0].input_data == "Find my project notes."


def test_planner_rejects_non_string_request() -> None:
    planner = DeterministicPlanner()

    with pytest.raises(ValueError, match="user_request must be a string"):
        planner.plan(123)


def test_deterministic_planner_is_deterministic() -> None:
    planner = DeterministicPlanner()

    first = planner.plan("same request")
    second = planner.plan("same request")

    assert first == second


def test_deterministic_planner_returns_execution_plan() -> None:
    planner = DeterministicPlanner()

    plan = planner.plan("test request")

    assert isinstance(plan, ExecutionPlan)
    assert plan.version == 1
    assert len(plan.steps) == 1
    assert plan.steps[0].capability == "respond"
