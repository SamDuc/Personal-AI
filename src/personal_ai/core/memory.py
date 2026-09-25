from dataclasses import dataclass
from datetime import datetime

from personal_ai.core.memory_lifecycle import MemoryLifecycleStatus
from personal_ai.core.memory_provenance_model import MemoryProvenance
from personal_ai.core.memory_types import MemoryType


@dataclass
class MemoryMetadata:
    """Additional metadata for a memory item."""

    source: str = "user"
    confidence: str = "explicit"
    sensitivity: str = "normal"


@dataclass
class Memory:
    """Canonical representation of a retained memory item."""

    id: str
    memory_type: MemoryType
    content: str

    provenance: MemoryProvenance

    created_at: datetime | None = None
    updated_at: datetime | None = None
    expires_at: datetime | None = None

    status: MemoryLifecycleStatus = MemoryLifecycleStatus.CANDIDATE
    sensitivity: str = "normal"

    metadata: MemoryMetadata | None = None
