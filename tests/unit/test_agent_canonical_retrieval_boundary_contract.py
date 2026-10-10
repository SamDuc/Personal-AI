from pathlib import Path


def test_agent_canonical_retrieval_boundary_contract_exists():
    path = Path(
        "docs/schemas/agent_canonical_retrieval_boundary.md"
    )

    assert path.exists()

    text = path.read_text(encoding="utf-8")

    required = [
        "RetrievalRequest",
        "RetrievalResult",
        "DataItem",
        "ContentIndex",
        "filesystem discovery",
        "content extraction",
        "lexical search",
        "semantic search",
        "access_policy",
        "fabricate retrieval results",
        "Version: 1",
    ]

    for term in required:
        assert term in text
