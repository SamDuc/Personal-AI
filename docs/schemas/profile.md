# Personal Profile Contract

## Purpose

Define the canonical representation of relatively stable information
about the user.

The profile is not a conversation history and must not be used as a
general-purpose memory store.

## Design Principles

1. Profile data represents relatively stable user context.
2. The user remains the authoritative source for personal information.
3. The system must not infer sensitive personal attributes.
4. Profile updates require an explicit trusted source or user confirmation.
5. LLM-generated suggestions must not directly overwrite profile data.
6. Profile data must remain separate from episodic and conversational memory.
7. Sensitive fields must have explicit sensitivity classification.
8. Profile access follows the central permission system.
9. The profile schema must remain independent of any LLM provider.
10. Schema changes must be versioned.

## Profile Entity

The canonical profile contains the following logical sections.

### Identity

Information needed to distinguish the profile within the system.

- `profile_id`
- `display_name`

Identity fields should remain minimal.

### Preferences

Relatively stable preferences that affect system behavior.

Examples:

- communication preferences
- output preferences
- tooling preferences
- workflow preferences

Preferences should describe explicit user choices rather than inferred
personality traits.

### Goals

Longer-term goals that may help the system provide relevant context.

Each goal may contain:

- `id`
- `title`
- `description`
- `status`
- `priority`
- `created_at`
- `updated_at`

### Skills

Known skills explicitly provided by the user or supported by reliable
evidence.

Each skill may contain:

- `name`
- `level`
- `source`
- `verified`

The system must distinguish explicit user-provided information from
automatically inferred information.

### Projects

Projects that the user explicitly associates with their profile.

Each project may contain:

- `id`
- `name`
- `description`
- `status`
- `topics`

Project-specific detailed information should remain in the project/data
systems rather than being duplicated in the profile.

### Environment

Technical or workflow environment relevant to assisting the user.

Examples:

- operating system
- development environment
- preferred tools
- programming languages
- hardware used for projects

Environment information should be treated as changeable and should
therefore include an update timestamp.

## Field Metadata

Profile fields should support provenance and update information.

Conceptually:

```yaml
value: ...
source: user
confidence: explicit
updated_at: "..."
sensitivity: normal
```

Possible source values:

- `user`
- `trusted_system`
- `external_source`

The system must not treat an LLM-generated guess as an authoritative
profile value.

## Sensitivity

Every profile field should have a sensitivity classification.

Allowed classifications:

- `normal`
- `private`
- `sensitive`
- `restricted`

Sensitive or restricted information must not automatically become
searchable general knowledge.

Credentials, passwords, private keys, authentication tokens, and similar
secrets must never be stored as ordinary profile data.

## Update Rules

Profile updates follow this flow:

```text
Candidate Update
      |
      v
Source Validation
      |
      v
Permission Check
      |
      v
User Confirmation when required
      |
      v
Profile Update
      |
      v
Audit Record
```

The LLM may propose an update but must not silently persist it.

## Relationship With Memory

Profile:

- relatively stable
- current user context
- explicit preferences and goals

Memory:

- historical events
- previous interactions
- decisions
- observations
- temporal context

A memory entry must not automatically become a profile fact.

## Relationship With DataItem

Profile information may reference projects or data resources, but the
unified `DataItem` model remains the canonical representation of external
resources.

The profile must not duplicate complete file, email, or cloud-resource
records.

## Versioning

The contract has an explicit schema version.

Initial version:

```yaml
version: 1
```

Breaking changes require a schema version change.

## Security Requirements

The system must:

- deny profile writes by default;
- avoid storing credentials and secrets;
- preserve provenance;
- preserve update timestamps;
- distinguish explicit facts from inferred information;
- prevent silent LLM profile mutation;
- support auditability.