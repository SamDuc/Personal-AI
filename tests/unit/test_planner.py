import pytest

from personal_ai.core.planner import DeterministicPlanner


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
