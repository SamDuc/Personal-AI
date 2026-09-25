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
from personal_ai.core.memory_validation import validate_memory


def create_test_memory(*, expires_at: datetime | None = None) -> Memory:
    recorded_at = datetime(2026, 9, 25, 12, 30, tzinfo=UTC)
    created_at = datetime(2026, 9, 25, 12, 31, tzinfo=UTC)
    updated_at = datetime(2026, 9, 25, 12, 32, tzinfo=UTC)

    return Memory(
        id="memory:integration:001",
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
        sensitivity="private",
        metadata=MemoryMetadata(
            source="auxiliary",
            confidence="high",
            sensitivity="normal",
        ),
    )


def test_validation_and_json_round_trip_preserve_semantic_memory():
    memory = create_test_memory(
        expires_at=datetime(2026, 12, 31, 23, 59, tzinfo=UTC)
    )

    validate_memory(memory)
    restored = memory_from_json(memory_to_json(memory))
    validate_memory(restored)

    assert restored == memory


def test_json_round_trip_preserves_provenance_and_enum_types():
    memory = create_test_memory(
        expires_at=datetime(2026, 12, 31, tzinfo=UTC)
    )
    restored = memory_from_json(memory_to_json(memory))

    assert restored.provenance == memory.provenance
    assert isinstance(restored.memory_type, MemoryType)
    assert isinstance(restored.provenance.source, MemorySource)
    assert isinstance(restored.provenance.method, MemoryProvenanceMethod)
    assert isinstance(restored.provenance.confidence, MemoryConfidence)
    assert isinstance(restored.status, MemoryLifecycleStatus)


def test_json_round_trip_preserves_timestamps_and_timezone():
    memory = create_test_memory(
        expires_at=datetime(2026, 12, 31, 23, 59, tzinfo=UTC)
    )
    restored = memory_from_json(memory_to_json(memory))

    assert restored.created_at == memory.created_at
    assert restored.updated_at == memory.updated_at
    assert restored.expires_at == memory.expires_at
    assert restored.provenance.recorded_at == memory.provenance.recorded_at
    assert restored.created_at.tzinfo == UTC
    assert restored.expires_at.tzinfo == UTC


def test_json_round_trip_preserves_none_expires_at():
    memory = create_test_memory()
    restored = memory_from_json(memory_to_json(memory))

    assert restored.expires_at is None


def test_metadata_round_trip_does_not_override_canonical_fields():
    memory = create_test_memory()
    restored = memory_from_json(memory_to_json(memory))

    assert restored.id == memory.id
    assert restored.memory_type is memory.memory_type
    assert restored.content == memory.content
    assert restored.provenance == memory.provenance
    assert restored.sensitivity == memory.sensitivity
    assert restored.metadata == memory.metadata


def test_canonical_json_uses_string_enum_values():
    data = json.loads(memory_to_json(create_test_memory()))
    persisted = data["memory"]

    assert persisted["memory_type"] == "semantic"
    assert persisted["status"] == "active"
    assert persisted["provenance"]["source"] == "user"
    assert persisted["provenance"]["method"] == "explicit"
    assert persisted["provenance"]["confidence"] == "explicit"


def test_invalid_persisted_json_is_rejected_at_boundary():
    with pytest.raises(ValueError, match="invalid JSON"):
        memory_from_json('{"version": 1,')


def test_tampered_persisted_representation_is_rejected():
    data = memory_to_dict(create_test_memory())
    data["memory"]["status"] = "not-a-lifecycle-state"

    with pytest.raises(ValueError, match="invalid lifecycle status"):
        memory_from_dict(data)


def test_unsupported_storage_version_is_rejected():
    data = memory_to_dict(create_test_memory())
    data["version"] = STORAGE_VERSION + 1

    with pytest.raises(
        ValueError,
        match="unsupported or missing storage version",
    ):
        memory_from_dict(data)
