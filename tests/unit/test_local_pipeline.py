from pathlib import Path

from personal_ai.connectors.local_file_content_extraction import (
    extract_local_file_content,
)
from personal_ai.connectors.local_file_source import discover_enabled_local_files
from personal_ai.connectors.local_filesystem import local_file_to_data_item
from personal_ai.core.models import AccessPolicy
from personal_ai.retrieval.local import RetrievalRequest, retrieve_local_items
from personal_ai.retrieval.local_integration import integrate_local_content_index
from personal_ai.sources.config import SourceConfig

SOURCES_PATH = Path("config/sources/sources.yaml")


def test_real_local_file_pipeline_to_retrieval(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text(
        "Personal AI vertical pipeline integration test",
        encoding="utf-8",
    )

    config = SourceConfig(
        {
            "sources": {
                "local_filesystem": {
                    "enabled": True,
                }
            }
        }
    )

    discovered = discover_enabled_local_files(tmp_path, config)

    assert len(discovered) == 1
    assert discovered[0].path == path

    item = local_file_to_data_item(discovered[0])

    assert item.source == "local_filesystem"
    assert item.source_id == str(path.resolve())
    assert item.content_available is False
    assert item.searchable is False

    item.access_policy = AccessPolicy(read=True, write=False)

    extracted = extract_local_file_content(path)

    assert extracted.content_available is True
    assert "vertical pipeline" in extracted.text

    item = integrate_local_content_index(item, extracted)

    assert item.content_available is True
    assert item.searchable is True
    assert item.content_ref is not None
    assert item.content_hash == extracted.content_hash
    assert item.sync_status == "indexed"

    results = retrieve_local_items(
        [item],
        RetrievalRequest(
            query="vertical pipeline",
            source="local_filesystem",
            limit=10,
        ),
    )

    assert len(results) == 1
    assert results[0].item.id == item.id
    assert results[0].item.content_ref == item.content_ref
