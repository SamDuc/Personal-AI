import json
from datetime import datetime

from personal_ai.core.memory import Memory, MemoryMetadata
from personal_ai.core.memory_lifecycle import MemoryLifecycleStatus
from personal_ai.core.memory_provenance import (
    MemoryConfidence,
    MemoryProvenanceMethod,
    MemorySource,
)
from personal_ai.core.memory_provenance_model import MemoryProvenance
from personal_ai.core.memory_types import MemoryType

STORAGE_VERSION = 1


def _serialize_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None

    return value.isoformat()


def _parse_datetime(value: str | None, field_name: str) -> datetime | None:
    if value is None:
        return None

    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be an ISO 8601 string or null")

    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} is malformed") from exc


def memory_to_dict(memory: Memory) -> dict:
    """Serialize a Memory into the canonical storage document."""
    provenance = memory.provenance

    return {
        "version": STORAGE_VERSION,
        "memory": {
            "id": memory.id,
            "memory_type": memory.memory_type.value,
            "content": memory.content,
            "provenance": {
                "source": provenance.source.value,
                "source_ref": provenance.source_ref,
                "method": provenance.method.value,
                "confidence": provenance.confidence.value,
                "recorded_at": _serialize_datetime(provenance.recorded_at),
            },
            "created_at": _serialize_datetime(memory.created_at),
            "updated_at": _serialize_datetime(memory.updated_at),
            "expires_at": _serialize_datetime(memory.expires_at),
            "status": memory.status.value,
            "sensitivity": memory.sensitivity,
            "metadata": (
                {
                    "source": memory.metadata.source,
                    "confidence": memory.metadata.confidence,
                    "sensitivity": memory.metadata.sensitivity,
                }
                if memory.metadata is not None
                else None
            ),
        },
    }


def memory_from_dict(data: dict) -> Memory:
    """Deserialize a canonical storage document into a Memory."""
    if not isinstance(data, dict):
        raise TypeError("storage document must be a dictionary")

    if data.get("version") != STORAGE_VERSION:
        raise ValueError("unsupported or missing storage version")

    memory_data = data.get("memory")
    if not isinstance(memory_data, dict):
        raise TypeError("memory must be a dictionary")

    required_fields = (
        "id",
        "memory_type",
        "content",
        "provenance",
        "status",
        "sensitivity",
    )

    for field_name in required_fields:
        if field_name not in memory_data:
            raise ValueError(f"missing memory field: {field_name}")

    if not isinstance(memory_data["id"], str) or not memory_data["id"]:
        raise ValueError("memory id must be a non-empty string")

    if not isinstance(memory_data["content"], str):
        raise TypeError("memory content must be a string")

    try:
        memory_type = MemoryType(memory_data["memory_type"])
    except (KeyError, ValueError) as exc:
        raise ValueError("invalid memory type") from exc

    provenance_data = memory_data["provenance"]
    if not isinstance(provenance_data, dict):
        raise TypeError("invalid provenance")

    provenance_fields = (
        "source",
        "source_ref",
        "method",
        "confidence",
        "recorded_at",
    )

    for field_name in provenance_fields:
        if field_name not in provenance_data:
            raise ValueError(f"missing provenance field: {field_name}")

    try:
        source = MemorySource(provenance_data["source"])
        method = MemoryProvenanceMethod(provenance_data["method"])
        confidence = MemoryConfidence(provenance_data["confidence"])
    except (KeyError, ValueError) as exc:
        raise ValueError("invalid provenance") from exc

    if not isinstance(provenance_data["source_ref"], str):
        raise TypeError("provenance source_ref must be a string")

    recorded_at = _parse_datetime(
        provenance_data["recorded_at"],
        "provenance.recorded_at",
    )

    if recorded_at is None:
        raise ValueError("provenance.recorded_at is required")

    provenance = MemoryProvenance(
        source=source,
        source_ref=provenance_data["source_ref"],
        method=method,
        confidence=confidence,
        recorded_at=recorded_at,
    )

    try:
        status = MemoryLifecycleStatus(memory_data["status"])
    except (KeyError, ValueError) as exc:
        raise ValueError("invalid lifecycle status") from exc

    sensitivity = memory_data["sensitivity"]
    if sensitivity not in {"normal", "private", "sensitive", "restricted"}:
        raise ValueError("invalid sensitivity")

    metadata_data = memory_data.get("metadata")
    metadata = None

    if metadata_data is not None:
        if not isinstance(metadata_data, dict):
            raise ValueError("metadata must be a dictionary or null")

        metadata = MemoryMetadata(
            source=metadata_data.get("source", "user"),
            confidence=metadata_data.get("confidence", "explicit"),
            sensitivity=metadata_data.get("sensitivity", "normal"),
        )

    return Memory(
        id=memory_data["id"],
        memory_type=memory_type,
        content=memory_data["content"],
        provenance=provenance,
        created_at=_parse_datetime(memory_data.get("created_at"), "created_at"),
        updated_at=_parse_datetime(memory_data.get("updated_at"), "updated_at"),
        expires_at=_parse_datetime(memory_data.get("expires_at"), "expires_at"),
        status=status,
        sensitivity=sensitivity,
        metadata=metadata,
    )


def memory_to_json(memory: Memory) -> str:
    """Serialize a Memory into canonical JSON."""
    return json.dumps(memory_to_dict(memory), ensure_ascii=False, separators=(",", ":"))


def memory_from_json(data: str) -> Memory:
    """Deserialize canonical JSON into a Memory."""
    if not isinstance(data, str):
        raise TypeError("JSON data must be a string")

    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as exc:
        raise ValueError("invalid JSON") from exc

    return memory_from_dict(parsed)
