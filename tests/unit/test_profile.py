from datetime import UTC, datetime

from personal_ai.core.profile import (
    Environment,
    Goal,
    Profile,
    ProfileField,
    ProfileMetadata,
    Project,
    Skill,
)


def test_profile_metadata_defaults():
    metadata = ProfileMetadata()

    assert metadata.source == "user"
    assert metadata.confidence == "explicit"
    assert metadata.updated_at is None
    assert metadata.sensitivity == "normal"


def test_profile_field_contains_metadata():
    field = ProfileField(value="dark")

    assert field.value == "dark"
    assert field.metadata.source == "user"
    assert field.metadata.confidence == "explicit"
    assert field.metadata.sensitivity == "normal"


def test_profile_entities_have_independent_metadata():
    goal = Goal(id="goal-1", title="Learn Python")
    skill = Skill(name="Python")
    project = Project(id="project-1", name="Personal AI")
    environment = Environment()

    goal.metadata.sensitivity = "private"

    assert skill.metadata.sensitivity == "normal"
    assert project.metadata.sensitivity == "normal"
    assert environment.metadata.sensitivity == "normal"


def test_profile_defaults():
    profile = Profile(profile_id="profile-001")

    assert profile.profile_id == "profile-001"
    assert profile.display_name is None
    assert profile.preferences == {}
    assert profile.goals == []
    assert profile.skills == []
    assert profile.projects == []

    assert isinstance(profile.environment, Environment)
    assert profile.environment.preferred_tools == []
    assert profile.environment.programming_languages == []
    assert profile.environment.hardware == []


def test_profile_with_real_metadata():
    updated = datetime(2026, 9, 25, 12, 0, tzinfo=UTC)

    profile = Profile(
        profile_id="profile-001",
        display_name=ProfileField(
            value="Example User",
            metadata=ProfileMetadata(
                source="user",
                confidence="explicit",
                updated_at=updated,
                sensitivity="normal",
            ),
        ),
        goals=[
            Goal(
                id="goal-1",
                title="Learn Python",
                priority="high",
            )
        ],
        skills=[
            Skill(
                name="Python",
                level="intermediate",
                verified=True,
            )
        ],
    )

    assert profile.display_name.value == "Example User"
    assert profile.display_name.metadata.updated_at == updated

    assert profile.goals[0].title == "Learn Python"
    assert profile.goals[0].metadata.source == "user"

    assert profile.skills[0].name == "Python"
    assert profile.skills[0].verified is True


def test_goal_contract_fields():
    created = datetime(2026, 9, 1, 10, 0, tzinfo=UTC)
    updated = datetime(2026, 9, 25, 12, 0, tzinfo=UTC)

    goal = Goal(
        id="goal-1",
        title="Learn Python",
        description="Build a solid Python foundation",
        status="active",
        priority="high",
        created_at=created,
        updated_at=updated,
    )

    assert goal.id == "goal-1"
    assert goal.title == "Learn Python"
    assert goal.description == "Build a solid Python foundation"
    assert goal.status == "active"
    assert goal.priority == "high"
    assert goal.created_at == created
    assert goal.updated_at == updated


def test_skill_contract_fields():
    skill = Skill(
        name="Python",
        level="intermediate",
        verified=True,
        metadata=ProfileMetadata(
            source="trusted_system",
            confidence="explicit",
            sensitivity="normal",
        ),
    )

    assert skill.name == "Python"
    assert skill.level == "intermediate"
    assert skill.verified is True
    assert skill.metadata.source == "trusted_system"


def test_project_contract_fields():
    project = Project(
        id="project-1",
        name="Personal AI",
        description="Local-first personal AI agent system",
        status="active",
        topics=["AI", "Python", "agents"],
    )

    assert project.id == "project-1"
    assert project.name == "Personal AI"
    assert project.description == "Local-first personal AI agent system"
    assert project.status == "active"
    assert project.topics == ["AI", "Python", "agents"]


def test_environment_contract_fields():
    updated = datetime(2026, 9, 25, 12, 0, tzinfo=UTC)

    environment = Environment(
        operating_system="Windows",
        development_environment="Conda",
        preferred_tools=["VS Code", "PowerShell"],
        programming_languages=["Python"],
        hardware=["PC"],
        metadata=ProfileMetadata(
            source="user",
            confidence="explicit",
            updated_at=updated,
            sensitivity="normal",
        ),
    )

    assert environment.operating_system == "Windows"
    assert environment.development_environment == "Conda"
    assert environment.preferred_tools == ["VS Code", "PowerShell"]
    assert environment.programming_languages == ["Python"]
    assert environment.hardware == ["PC"]
    assert environment.metadata.updated_at == updated
