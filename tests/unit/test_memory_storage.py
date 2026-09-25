import json
from datetime import UTC, datetime

import pytest

from personal_ai.core.memory import Memory, MemoryMetadata
from personal_ai.core.memory_lifecycle import MemoryLifecycleStatus
from personal_ai.core.memory_provenance import (
    MemoryConfidence,
    MemoryProvenanceMethod,
    MemorySource,
)
from personal_ai.core.memory_provenance_model import MemoryProvenance
from personal_ai.core.memory_storage import (
    STORAGE_VERSION,
    memory_from_dict,
    memory_from_json,
    memory_to_dict,
    memory_to_json,
)
from personal_ai.core.memory_types import MemoryType


def create_test_memory() -> Memory:
    recorded_at = datetime(2026, 9, 25, 12, 30, 0, tzinfo=UTC)
    created_at = datetime(2026, 9, 25, 12, 31, 0, tzinfo=UTC)
    updated_at = datetime(2026, 9, 25, 12, 32, 0, tzinfo=UTC)
    expires_at = datetime(2026, 12, 31, 23, 59, 59, tzinfo=UTC)

    return Memory(
        id="memory:test:001",
        memory_type=MemoryType.SEMANTIC,
        content="User prefers local-first architecture.",
        provenance=MemoryProvenance(
            source=MemorySource.USER,
            source_ref="test:user_input",
            method=MemoryProvenanceMethod.EXPLICIT,
            confidence=MemoryConfidence.EXPLICIT,
            recorded_at=recorded_at,
        ),
        created_at=created_at,
        updated_at=updated_at,
        expires_at=expires_at,
        status=MemoryLifecycleStatus.ACTIVE,
        sensitivity="normal",
        metadata=MemoryMetadata(
            source="user",
            confidence="explicit",
            sensitivity="normal",
        ),
    )


def test_memory_to_dict_contains_canonical_storage_structure():
    data = memory_to_dict(create_test_memory())

    assert data["version"] == STORAGE_VERSION
    assert set(data) == {"version", "memory"}

    memory_data = data["memory"]

    assert memory_data["id"] == "memory:test:001"
    assert memory_data["memory_type"] == "semantic"
    assert memory_data["content"] == "User prefers local-first architecture."
    assert memory_data["status"] == "active"
    assert memory_data["sensitivity"] == "normal"


def test_memory_to_dict_preserves_provenance():
    data = memory_to_dict(create_test_memory())
    provenance = data["memory"]["provenance"]

    assert provenance == {
        "source": "user",
        "source_ref": "test:user_input",
        "method": "explicit",
        "confidence": "explicit",
        "recorded_at": "2026-09-25T12:30:00+00:00",
    }


def test_memory_to_dict_preserves_timestamps():
    data = memory_to_dict(create_test_memory())
    memory_data = data["memory"]

    assert memory_data["created_at"] == "2026-09-25T12:31:00+00:00"
    assert memory_data["updated_at"] == "2026-09-25T12:32:00+00:00"
    assert memory_data["expires_at"] == "2026-12-31T23:59:59+00:00"


def test_memory_to_dict_preserves_metadata():
    data = memory_to_dict(create_test_memory())

    assert data["memory"]["metadata"] == {
        "source": "user",
        "confidence": "explicit",
        "sensitivity": "normal",
    }


def test_memory_from_dict_reconstructs_memory():
    original = create_test_memory()

    restored = memory_from_dict(memory_to_dict(original))

    assert restored == original
    assert restored is not original
    assert restored.provenance is not original.provenance


def test_memory_to_json_returns_valid_json():
    memory = create_test_memory()

    data = json.loads(memory_to_json(memory))

    assert data["version"] == STORAGE_VERSION
    assert data["memory"]["id"] == memory.id


def test_memory_from_json_reconstructs_memory():
    original = create_test_memory()

    restored = memory_from_json(memory_to_json(original))

    assert restored == original
    assert restored is not original


def test_memory_json_round_trip_preserves_semantics():
    original = create_test_memory()

    restored = memory_from_json(memory_to_json(original))

    assert restored.id == original.id
    assert restored.memory_type is original.memory_type
    assert restored.content == original.content
    assert restored.provenance == original.provenance
    assert restored.created_at == original.created_at
    assert restored.updated_at == original.updated_at
    assert restored.expires_at == original.expires_at
    assert restored.status is original.status
    assert restored.sensitivity == original.sensitivity
    assert restored.metadata == original.metadata


def test_memory_from_dict_rejects_missing_version():
    data = memory_to_dict(create_test_memory())
    del data["version"]

    with pytest.raises(ValueError):
        memory_from_dict(data)


def test_memory_from_dict_rejects_unsupported_version():
    data = memory_to_dict(create_test_memory())
    data["version"] = STORAGE_VERSION + 1

    with pytest.raises(ValueError):
        memory_from_dict(data)


def test_memory_from_dict_rejects_missing_memory():
    with pytest.raises(TypeError):
        memory_from_dict({"version": STORAGE_VERSION})


def test_memory_from_json_rejects_invalid_json():
    with pytest.raises(ValueError):
        memory_from_json("{invalid json")


def test_memory_from_json_rejects_non_string_input():
    with pytest.raises(TypeError):
        memory_from_json(123)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "field",
    [
        "id",
        "memory_type",
        "content",
        "provenance",
        "status",
        "sensitivity",
    ],
)
def test_memory_from_dict_rejects_missing_required_memory_field(field):
    data = memory_to_dict(create_test_memory())
    del data["memory"][field]

    with pytest.raises(ValueError):
        memory_from_dict(data)


def test_memory_from_dict_rejects_invalid_memory_type():
    data = memory_to_dict(create_test_memory())
    data["memory"]["memory_type"] = "invalid"

    with pytest.raises(ValueError):
        memory_from_dict(data)


def test_memory_from_dict_rejects_invalid_lifecycle_status():
    data = memory_to_dict(create_test_memory())
    data["memory"]["status"] = "invalid"

    with pytest.raises(ValueError):
        memory_from_dict(data)


def test_memory_from_dict_rejects_invalid_sensitivity():
    data = memory_to_dict(create_test_memory())
    data["memory"]["sensitivity"] = "invalid"

    with pytest.raises(ValueError):
        memory_from_dict(data)


def test_memory_from_dict_rejects_malformed_timestamp():
    data = memory_to_dict(create_test_memory())
    data["memory"]["created_at"] = "not-a-timestamp"

    with pytest.raises(ValueError):
        memory_from_dict(data)


def test_memory_from_dict_rejects_invalid_provenance():
    data = memory_to_dict(create_test_memory())
    data["memory"]["provenance"]["source"] = "invalid"

    with pytest.raises(ValueError):
        memory_from_dict(data)


def test_memory_from_dict_rejects_missing_recorded_at():
    data = memory_to_dict(create_test_memory())
    del data["memory"]["provenance"]["recorded_at"]

    with pytest.raises(ValueError):
        memory_from_dict(data)
