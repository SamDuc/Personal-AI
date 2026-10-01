from pathlib import Path


def test_consistency_contract_exists() -> None:
    path = Path("docs/schemas/local_source_index_consistency.md")

    assert path.exists()

    text = path.read_text(encoding="utf-8")

    required_sections = [
        "## 1. Purpose",
        "## 2. Source Identity",
        "## 3. Source Snapshot",
        "## 4. Index Timestamp",
        "## 5. Content Hash",
        "## 6. Consistency States",
        "## 7. Consistency Resolution",
        "## 8. Refresh Boundary",
        "## 9. Missing Source",
        "## 10. Unavailable Source",
        "## 11. Retrieval Boundary",
        "## 12. Permission Boundary",
        "## 13. Source Authority",
        "## 14. Separation of Responsibilities",
        "## 15. Read-Only Behavior",
        "## 16. Determinism",
        "## 17. Contract Version",
    ]

    for section in required_sections:
        assert section in text


def test_consistency_contract_keeps_refresh_outside_resolution() -> None:
    path = Path("docs/schemas/local_source_index_consistency.md")
    text = path.read_text(encoding="utf-8")

    assert "Consistency resolution MUST NOT" in text
    assert "automatically re-index content" in text
    assert "extract file content" in text
    assert "Refreshing an out-of-sync representation is a separate" in text


def test_consistency_contract_preserves_filesystem_authority() -> None:
    path = Path("docs/schemas/local_source_index_consistency.md")
    text = path.read_text(encoding="utf-8")

    assert "The filesystem remains authoritative." in text
    assert "The indexed representation remains derived." in text
    assert "MUST NOT become the authority" in text


def test_consistency_contract_defines_required_states() -> None:
    path = Path("docs/schemas/local_source_index_consistency.md")
    text = path.read_text(encoding="utf-8")

    for state in (
        "`consistent`",
        "`out_of_sync`",
        "`source_missing`",
        "`source_unavailable`",
    ):
        assert state in text
