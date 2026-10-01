from pathlib import Path


def test_agent_capability_boundary_contract_exists():
    path = Path("docs/schemas/agent_capability_boundary.md")

    assert path.exists()

    text = path.read_text(encoding="utf-8")

    required = [
        "Planner",
        "ExecutionPlan",
        "Executor",
        "supplied Capability",
        "LLM providers",
        "retrievers",
        "filesystem access",
        "permission evaluators",
        "unknown capabilities",
        "fabricate results",
        "Version: 1",
    ]

    for term in required:
        assert term in text
