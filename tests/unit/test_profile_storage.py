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
from personal_ai.core.profile_storage import ProfileSerializer


def test_profile_to_dict_contains_storage_envelope():
    profile = Profile(profile_id='profile-001')

    data = ProfileSerializer.to_dict(profile)

    assert data['version'] == 1
    assert data['profile']['profile_id'] == 'profile-001'


def test_profile_to_dict_preserves_nested_profile_data():
    updated = datetime(2026, 9, 25, 12, 0, tzinfo=UTC)

    profile = Profile(
        profile_id='profile-001',
        display_name=ProfileField(
            value='Example User',
            metadata=ProfileMetadata(
                source='user',
                confidence='explicit',
                updated_at=updated,
                sensitivity='normal',
            ),
        ),
        preferences={
            'theme': ProfileField(value='dark'),
        },
        goals=[
            Goal(
                id='goal-1',
                title='Learn Python',
                priority='high',
            )
        ],
        skills=[
            Skill(
                name='Python',
                level='intermediate',
                verified=True,
            )
        ],
        projects=[
            Project(
                id='project-1',
                name='Personal AI',
                status='active',
                topics=['AI', 'Python'],
            )
        ],
        environment=Environment(
            operating_system='Windows',
            development_environment='Conda',
            preferred_tools=['VS Code', 'PowerShell'],
            programming_languages=['Python'],
            hardware=['PC'],
            metadata=ProfileMetadata(
                updated_at=updated,
            ),
        ),
    )

    data = ProfileSerializer.to_dict(profile)

    assert data['profile']['display_name']['value'] == 'Example User'
    assert data['profile']['display_name']['metadata']['updated_at'] == (
        '2026-09-25T12:00:00+00:00'
    )

    assert data['profile']['preferences']['theme']['value'] == 'dark'
    assert data['profile']['goals'][0]['title'] == 'Learn Python'
    assert data['profile']['skills'][0]['name'] == 'Python'
    assert data['profile']['projects'][0]['name'] == 'Personal AI'
    assert data['profile']['environment']['operating_system'] == 'Windows'


def test_dict_to_profile_reconstructs_typed_objects():
    data = {
        'version': 1,
        'profile': {
            'profile_id': 'profile-001',
            'display_name': {
                'value': 'Example User',
                'metadata': {
                    'source': 'user',
                    'confidence': 'explicit',
                    'updated_at': '2026-09-25T12:00:00+00:00',
                    'sensitivity': 'normal',
                },
            },
            'preferences': {},
            'goals': [],
            'skills': [],
            'projects': [],
            'environment': {
                'operating_system': 'Windows',
                'development_environment': 'Conda',
                'preferred_tools': [],
                'programming_languages': ['Python'],
                'hardware': [],
                'metadata': {
                    'source': 'user',
                    'confidence': 'explicit',
                    'updated_at': None,
                    'sensitivity': 'normal',
                },
            },
        },
    }

    profile = ProfileSerializer.from_dict(data)

    assert isinstance(profile, Profile)
    assert isinstance(profile.display_name, ProfileField)
    assert isinstance(profile.display_name.metadata, ProfileMetadata)
    assert isinstance(profile.environment, Environment)
    assert profile.display_name.metadata.updated_at == datetime(
        2026, 9, 25, 12, 0, tzinfo=UTC
    )


def test_profile_round_trip_preserves_semantic_values():
    updated = datetime(2026, 9, 25, 12, 0, tzinfo=UTC)

    original = Profile(
        profile_id='profile-001',
        display_name=ProfileField(
            value='Example User',
            metadata=ProfileMetadata(updated_at=updated),
        ),
        preferences={
            'theme': ProfileField(value='dark'),
        },
        goals=[
            Goal(
                id='goal-1',
                title='Learn Python',
                priority='high',
            )
        ],
        skills=[
            Skill(
                name='Python',
                level='intermediate',
                verified=True,
            )
        ],
        projects=[
            Project(
                id='project-1',
                name='Personal AI',
                topics=['AI', 'Python'],
            )
        ],
        environment=Environment(
            operating_system='Windows',
            programming_languages=['Python'],
            hardware=['PC'],
            metadata=ProfileMetadata(updated_at=updated),
        ),
    )

    restored = ProfileSerializer.from_dict(
        ProfileSerializer.to_dict(original)
    )

    assert restored == original


def test_deserialized_mutable_values_are_independent():
    original = Profile(
        profile_id='profile-001',
        preferences={
            'theme': ProfileField(value='dark'),
        },
    )

    restored = ProfileSerializer.from_dict(
        ProfileSerializer.to_dict(original)
    )

    restored.preferences['theme'].value = 'light'

    assert original.preferences['theme'].value == 'dark'
    assert restored.preferences['theme'].value == 'light'
import pytest


def test_to_json_and_from_json_round_trip():
    original = Profile(profile_id='profile-001')

    serialized = ProfileSerializer.to_json(original)
    restored = ProfileSerializer.from_json(serialized)

    assert restored == original


def test_from_dict_rejects_missing_version():
    with pytest.raises(ValueError, match='Missing storage version'):
        ProfileSerializer.from_dict({
            'profile': {'profile_id': 'profile-001'},
        })


def test_from_dict_rejects_unsupported_version():
    with pytest.raises(ValueError, match='Unsupported storage version'):
        ProfileSerializer.from_dict({
            'version': 999,
            'profile': {'profile_id': 'profile-001'},
        })


def test_from_dict_rejects_missing_profile():
    with pytest.raises(ValueError, match='Missing profile'):
        ProfileSerializer.from_dict({
            'version': 1,
        })


def test_from_dict_rejects_non_object_profile():
    with pytest.raises(TypeError, match='Profile must be an object'):
        ProfileSerializer.from_dict({
            'version': 1,
            'profile': [],
        })


def test_from_dict_rejects_missing_profile_id():
    with pytest.raises(ValueError, match='Missing profile_id'):
        ProfileSerializer.from_dict({
            'version': 1,
            'profile': {},
        })

def test_from_dict_rejects_non_object_input():
    with pytest.raises(TypeError, match='Storage data must be an object'):
        ProfileSerializer.from_dict([])


def test_from_dict_rejects_malformed_goal():
    with pytest.raises(ValueError, match='Malformed goal'):
        ProfileSerializer.from_dict({
            'version': 1,
            'profile': {
                'profile_id': 'profile-001',
                'goals': [
                    {'id': 'goal-1'},
                ],
                'environment': {
                    'metadata': {
                        'source': 'user',
                        'confidence': 'explicit',
                        'updated_at': None,
                        'sensitivity': 'normal',
                    },
                },
            },
        })


def test_from_dict_rejects_malformed_metadata():
    with pytest.raises(ValueError, match='Malformed metadata'):
        ProfileSerializer.from_dict({
            'version': 1,
            'profile': {
                'profile_id': 'profile-001',
                'environment': {
                    'metadata': {},
                },
            },
        })


def test_from_dict_rejects_malformed_preferences():
    with pytest.raises(TypeError, match='Preferences must be an object'):
        ProfileSerializer.from_dict({
            'version': 1,
            'profile': {
                'profile_id': 'profile-001',
                'preferences': [],
            },
        })


def test_from_json_rejects_non_object_json():
    with pytest.raises(TypeError, match='Storage data must be an object'):
        ProfileSerializer.from_json('[]')


def test_from_json_rejects_invalid_json():
    with pytest.raises(ValueError):
        ProfileSerializer.from_json('{invalid json')
