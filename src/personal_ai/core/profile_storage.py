from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from typing import Any

from personal_ai.core.profile import (
    Environment,
    Goal,
    Profile,
    ProfileField,
    ProfileMetadata,
    Project,
    Skill,
)


class ProfileSerializer:
    VERSION = 1

    @staticmethod
    def _datetime_to_value(value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.isoformat()

    @staticmethod
    def _datetime_from_value(value: str | None) -> datetime | None:
        if value is None:
            return None
        return datetime.fromisoformat(value)

    @classmethod
    def _metadata_from_dict(
        cls,
        data: dict[str, Any],
    ) -> ProfileMetadata:
        if not isinstance(data, dict):
            raise TypeError('Metadata must be an object.')

        required = {
            'source',
            'confidence',
            'updated_at',
            'sensitivity',
        }

        if not required.issubset(data):
            raise ValueError('Malformed metadata.')

        return ProfileMetadata(
            source=data['source'],
            confidence=data['confidence'],
            updated_at=cls._datetime_from_value(data['updated_at']),
            sensitivity=data['sensitivity'],
        )

    @classmethod
    def _field_from_dict(
        cls,
        data: dict[str, Any],
    ) -> ProfileField:
        return ProfileField(
            value=data['value'],
            metadata=cls._metadata_from_dict(data['metadata']),
        )

    @classmethod
    def _goal_from_dict(
        cls,
        data: dict[str, Any],
    ) -> Goal:
        if not isinstance(data, dict):
            raise TypeError('Goal must be an object.')

        required_fields = {
            'id',
            'title',
            'description',
            'status',
            'priority',
            'created_at',
            'updated_at',
            'metadata',
        }

        if not required_fields.issubset(data):
            raise ValueError('Malformed goal.')

        return Goal(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            status=data['status'],
            priority=data['priority'],
            created_at=cls._datetime_from_value(data['created_at']),
            updated_at=cls._datetime_from_value(data['updated_at']),
            metadata=cls._metadata_from_dict(data['metadata']),
        )

    @classmethod
    def to_dict(
        cls,
        profile: Profile,
    ) -> dict[str, Any]:
        profile_data = asdict(profile)

        def convert(value: Any) -> Any:
            if isinstance(value, datetime):
                return cls._datetime_to_value(value)

            if isinstance(value, dict):
                return {
                    key: convert(item)
                    for key, item in value.items()
                }

            if isinstance(value, list):
                return [convert(item) for item in value]

            return value

        return {
            'version': cls.VERSION,
            'profile': convert(profile_data),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> Profile:
        if not isinstance(data, dict):
            raise TypeError('Storage data must be an object.')

        if 'version' not in data:
            raise ValueError('Missing storage version.')

        if data['version'] != cls.VERSION:
            raise ValueError(
                f'Unsupported storage version: {data["version"]!r}'
            )

        if 'profile' not in data:
            raise ValueError('Missing profile.')

        profile_data = data['profile']

        if not isinstance(profile_data, dict):
            raise TypeError('Profile must be an object.')

        if 'profile_id' not in profile_data:
            raise ValueError('Missing profile_id.')

        display_name = profile_data.get('display_name')
        preferences = profile_data.get('preferences', {})

        if not isinstance(preferences, dict):
            raise TypeError('Preferences must be an object.')

        return Profile(
            profile_id=profile_data['profile_id'],
            display_name=(
                cls._field_from_dict(display_name)
                if display_name is not None
                else None
            ),
            preferences={
                key: cls._field_from_dict(value)
                for key, value in preferences.items()
            },
            goals=[
                cls._goal_from_dict(item)
                for item in profile_data.get('goals', [])
            ],
            skills=[
                Skill(
                    name=item['name'],
                    level=item['level'],
                    verified=item['verified'],
                    metadata=cls._metadata_from_dict(
                        item['metadata']
                    ),
                )
                for item in profile_data.get('skills', [])
            ],
            projects=[
                Project(
                    id=item['id'],
                    name=item['name'],
                    description=item['description'],
                    status=item['status'],
                    topics=list(item['topics']),
                    metadata=cls._metadata_from_dict(
                        item['metadata']
                    ),
                )
                for item in profile_data.get('projects', [])
            ],
            environment=cls._environment_from_dict(
                profile_data.get('environment', {})
            ),
        )

    @classmethod
    def _environment_from_dict(
        cls,
        data: dict[str, Any],
    ) -> Environment:
        return Environment(
            operating_system=data.get('operating_system'),
            development_environment=data.get(
                'development_environment'
            ),
            preferred_tools=list(
                data.get('preferred_tools', [])
            ),
            programming_languages=list(
                data.get('programming_languages', [])
            ),
            hardware=list(data.get('hardware', [])),
            metadata=cls._metadata_from_dict(data['metadata']),
        )

    @classmethod
    def to_json(cls, profile: Profile) -> str:
        return json.dumps(
            cls.to_dict(profile),
            ensure_ascii=False,
            indent=2,
        )

    @classmethod
    def from_json(cls, value: str) -> Profile:
        data = json.loads(value)
        return cls.from_dict(data)