from pathlib import Path


def test_canonical_retrieval_resource_contract_exists():
    path = Path("docs/schemas/canonical_retrieval_resource.md")
    assert path.exists()

    text = path.read_text(encoding="utf-8")

    required = [
        "DataItem",
        "RetrievalRequest",
        "RetrievalResult",
        "sync_status",
        "access_policy.read",
        "implementation details",
        "Version: 1",
    ]

    for term in required:
        assert term in text
