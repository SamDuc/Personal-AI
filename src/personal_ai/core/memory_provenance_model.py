from dataclasses import dataclass
from datetime import datetime

from personal_ai.core.memory_provenance import (
    MemoryConfidence,
    MemoryProvenanceMethod,
    MemorySource,
)


@dataclass
class MemoryProvenance:
    """Provenance information for a memory item."""

    source: MemorySource
    source_ref: str
    method: MemoryProvenanceMethod
    confidence: MemoryConfidence
    recorded_at: datetime