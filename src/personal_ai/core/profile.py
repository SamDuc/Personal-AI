from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ProfileMetadata:
    """Provenance, confidence, update time, and sensitivity for profile data."""

    source: str = "user"
    confidence: str = "explicit"
    updated_at: datetime | None = None
    sensitivity: str = "normal"


@dataclass
class ProfileField:
    """A profile value with provenance and sensitivity metadata."""

    value: Any
    metadata: ProfileMetadata = field(default_factory=ProfileMetadata)


@dataclass
class Goal:
    """A longer-term user goal."""

    id: str
    title: str
    description: str | None = None
    status: str = "active"
    priority: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    metadata: ProfileMetadata = field(default_factory=ProfileMetadata)


@dataclass
class Skill:
    """A known user skill with provenance."""

    name: str
    level: str | None = None
    verified: bool = False
    metadata: ProfileMetadata = field(default_factory=ProfileMetadata)


@dataclass
class Project:
    """A project explicitly associated with the profile."""

    id: str
    name: str
    description: str | None = None
    status: str | None = None
    topics: list[str] = field(default_factory=list)
    metadata: ProfileMetadata = field(default_factory=ProfileMetadata)


@dataclass
class Environment:
    """Technical or workflow environment information."""

    operating_system: str | None = None
    development_environment: str | None = None
    preferred_tools: list[str] = field(default_factory=list)
    programming_languages: list[str] = field(default_factory=list)
    hardware: list[str] = field(default_factory=list)
    metadata: ProfileMetadata = field(default_factory=ProfileMetadata)


@dataclass
class Profile:
    """Canonical representation of relatively stable user context."""

    profile_id: str
    display_name: ProfileField | None = None

    preferences: dict[str, ProfileField] = field(default_factory=dict)
    goals: list[Goal] = field(default_factory=list)
    skills: list[Skill] = field(default_factory=list)
    projects: list[Project] = field(default_factory=list)

    environment: Environment = field(default_factory=Environment)