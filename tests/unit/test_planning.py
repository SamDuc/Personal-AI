import pytest

from personal_ai.core.planning import ExecutionPlan, PlanStep


def test_plan_step_requires_identity() -> None:
    with pytest.raises(ValueError, match="step_id"):
        PlanStep(step_id="", capability="respond")


def test_plan_step_requires_capability() -> None:
    with pytest.raises(ValueError, match="capability"):
        PlanStep(step_id="step-1", capability="")


def test_execution_plan_preserves_request() -> None:
    plan = ExecutionPlan(
        plan_id="plan-1",
        original_request="Find my architecture notes.",
        steps=(
            PlanStep(
                step_id="step-1",
                capability="respond",
            ),
        ),
    )

    assert plan.original_request == "Find my architecture notes."


def test_execution_plan_rejects_duplicate_steps() -> None:
    with pytest.raises(ValueError, match="duplicate step_id"):
        ExecutionPlan(
            plan_id="plan-1",
            original_request="request",
            steps=(
                PlanStep("step-1", "a"),
                PlanStep("step-1", "b"),
            ),
        )


def test_execution_plan_rejects_invalid_version() -> None:
    with pytest.raises(ValueError, match="unsupported plan version"):
        ExecutionPlan(
            plan_id="plan-1",
            original_request="request",
            steps=(),
            version=99,
        )


def test_execution_plan_is_immutable() -> None:
    plan = ExecutionPlan(
        plan_id="plan-1",
        original_request="request",
        steps=(),
    )

    with pytest.raises(AttributeError):
        plan.plan_id = "changed"


