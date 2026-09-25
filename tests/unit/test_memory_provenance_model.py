from datetime import UTC, datetime

from personal_ai.core.memory_provenance import (
    MemoryConfidence,
    MemoryProvenanceMethod,
    MemorySource,
)
from personal_ai.core.memory_provenance_model import MemoryProvenance


def test_memory_provenance_can_be_created():
    recorded_at = datetime.now(UTC)

    provenance = MemoryProvenance(
        source=MemorySource.USER,
        source_ref="user_input",
        method=MemoryProvenanceMethod.EXPLICIT,
        confidence=MemoryConfidence.EXPLICIT,
        recorded_at=recorded_at,
    )

    assert provenance.source == MemorySource.USER
    assert provenance.source_ref == "user_input"
    assert provenance.method == MemoryProvenanceMethod.EXPLICIT
    assert provenance.confidence == MemoryConfidence.EXPLICIT
    assert provenance.recorded_at == recorded_at


def test_memory_provenance_preserves_source_reference():
    provenance = MemoryProvenance(
        source=MemorySource.EXTERNAL_SOURCE,
        source_ref="document:example.txt",
        method=MemoryProvenanceMethod.IMPORTED,
        confidence=MemoryConfidence.HIGH,
        recorded_at=datetime.now(UTC),
    )

    assert provenance.source_ref == "document:example.txt"


def test_memory_provenance_supports_derived_memory():
    provenance = MemoryProvenance(
        source=MemorySource.TRUSTED_SYSTEM,
        source_ref="system:profile",
        method=MemoryProvenanceMethod.DERIVED,
        confidence=MemoryConfidence.MEDIUM,
        recorded_at=datetime.now(UTC),
    )

    assert provenance.method == MemoryProvenanceMethod.DERIVED
    assert provenance.confidence == MemoryConfidence.MEDIUM


def test_memory_provenance_is_dataclass():
    provenance = MemoryProvenance(
        source=MemorySource.USER,
        source_ref="user_input",
        method=MemoryProvenanceMethod.EXPLICIT,
        confidence=MemoryConfidence.EXPLICIT,
        recorded_at=datetime.now(UTC),
    )

    assert provenance.__dataclass_fields__.keys() == {
        "source",
        "source_ref",
        "method",
        "confidence",
        "recorded_at",
    }