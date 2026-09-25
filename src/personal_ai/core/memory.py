from dataclasses import dataclass
from datetime import datetime

from personal_ai.core.memory_types import MemoryType


@dataclass
class MemoryMetadata:
    """Provenance, confidence, and sensitivity for a memory item."""

    source: str = "user"
    confidence: str = "explicit"
    sensitivity: str = "normal"


@dataclass
class Memory:
    """Canonical representation of a retained memory item."""

    id: str
    memory_type: MemoryType
    content: str

    source: str = "user"
    confidence: str = "explicit"

    created_at: datetime | None = None
    updated_at: datetime | None = None
    expires_at: datetime | None = None

    status: str = "candidate"
    sensitivity: str = "normal"

    metadata: MemoryMetadata | None = None
