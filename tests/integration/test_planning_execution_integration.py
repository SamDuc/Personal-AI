from personal_ai.core.executor import Executor
from personal_ai.core.planner import DeterministicPlanner


def test_planning_execution_pipeline() -> None:
    planner = DeterministicPlanner()

    plan = planner.plan("Run a safe operation.")

    executor = Executor(
        {
            "respond": lambda value: f"executed: {value}",
        }
    )

    results = executor.execute(plan)

    assert results == ["executed: Run a safe operation."]
    assert plan.original_request == "Run a safe operation."
