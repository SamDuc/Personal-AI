# Profile Storage Contract

## Purpose

Define the persistence contract for the Personal AI profile.

The storage layer is responsible for serializing and restoring the canonical Profile model without changing its meaning.

## Storage Format

The canonical persistence format is JSON.

The stored document must contain:

- version: 1
- profile: {}

## Versioning

The storage document must contain a top-level version.

Initial version: 1

Breaking storage-format changes require a version change.

Unknown versions must be rejected rather than silently interpreted.

## Profile Identity

The stored profile must contain profile_id.

A profile document without profile_id is invalid.

## Serialization Rules

The serializer must preserve:

- profile identity
- display name
- preferences
- goals
- skills
- projects
- environment
- profile metadata
- provenance
- confidence
- sensitivity
- update timestamps

Datetime values must be serialized into a standard ISO 8601 representation.

Timezone information must be preserved when present.

## Deserialization Rules

Loading a profile must reconstruct the canonical Profile model.

The following must remain typed objects:

- Profile
- ProfileField
- ProfileMetadata
- Goal
- Skill
- Project
- Environment

Serialized lists and dictionaries must be reconstructed as independent mutable objects.

## Round-Trip Requirement

For a valid profile:

Profile -> serialize -> JSON -> deserialize -> Profile

must preserve the semantic values of the original profile.

## Validation

The storage layer must reject:

- missing version
- unsupported version
- missing profile
- missing profile_id
- malformed profile data

Validation errors must be explicit.

## Security

The storage layer must not:

- store credentials
- store passwords
- store private keys
- store authentication tokens
- silently add inferred sensitive information

The storage layer does not grant permissions.

Permissions remain the responsibility of the central permission layer.

## Scope

This contract does not define:

- database storage
- cloud synchronization
- encryption
- memory storage
- LLM integration
- profile update authorization
- audit logging

Those responsibilities belong to other system components.
