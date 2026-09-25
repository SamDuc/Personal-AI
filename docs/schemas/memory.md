# Memory Contract

## Purpose

Define the canonical contract for memory in the Personal AI system.

Memory stores information that may be useful for future interactions or tasks.

Memory is distinct from:

- Profile
- Source data
- Working task state

The memory layer must not replace the Profile model and must not become a duplicate storage layer for source data.

## Design Principles

Memory must:

- preserve provenance
- preserve confidence
- preserve timestamps
- preserve sensitivity
- support lifecycle management
- remain independent of any LLM
- remain independent of a database or vector store
- remain compatible with local-first architecture
- preserve the authoritative source of information
- support future retrieval without requiring a specific retrieval technology

## Memory Identity

Every memory item must have:

- id

The id uniquely identifies the memory item within the memory system.

## Memory Classification

Memory must support an explicit memory type.

Initial memory types:

- semantic
- episodic
- working
- procedural

The memory type describes the role of the memory and must not be inferred silently from content.

## Memory Content

Every memory item must contain content representing the information stored by the memory system.

Content must remain independent of:

- LLM provider
- embedding provider
- vector database
- retrieval implementation

## Provenance

Every memory item must preserve provenance.

Provenance must distinguish information supplied by the user from information obtained from trusted systems or other sources.

Initial provenance sources:

- user
- trusted_system
- external_source

Model inference must not automatically become authoritative user information.

## Confidence

Memory must preserve confidence information.

Confidence must distinguish explicitly provided information from information that is inferred or otherwise less certain.

The memory system must not silently upgrade inferred information into explicit user-provided information.

## Timestamps

Memory must preserve:

- created_at
- updated_at

Memory types that require expiration may additionally contain:

- expires_at

Datetime values must preserve timezone information when present.

## Lifecycle

A memory item must have an explicit lifecycle status.

Initial lifecycle states:

- candidate
- active
- superseded
- archived
- expired

Lifecycle transitions must be explicit.

A newer memory must not require immediate physical deletion of an older memory.

Where appropriate, an older memory may become superseded while remaining available for audit or historical reasoning.

## Sensitivity

Memory must have an explicit sensitivity classification.

Initial values:

- normal
- private
- sensitive
- restricted

The memory system must not infer sensitive personal attributes from incomplete evidence and store them as authoritative memory.

## Profile Relationship

Memory and Profile are separate concepts.

Profile represents relatively stable user context.

Memory represents information retained for future use.

A memory may refer to information related to the Profile, but Profile data must not be silently copied into Memory merely because it exists in the Profile.

Profile remains authoritative for profile information.

## Source Data Relationship

Memory is not a replacement for source data.

When memory originates from a source item:

- the source remains authoritative
- memory should preserve provenance
- the memory should reference the source where applicable
- the system must not treat a derived memory as the original source

## Updates

Memory updates must preserve provenance and timestamps.

An update must not silently erase the historical meaning of an existing memory.

When information changes, the system may create a new memory and mark the previous memory as superseded.

## Security

The memory layer must not:

- store passwords
- store authentication tokens
- store private keys
- treat credentials as ordinary memory
- grant permissions
- perform external actions

Permissions remain the responsibility of the central permission layer.

## Persistence

The canonical persistence format for the initial memory implementation will be JSON.

The storage document must contain:

- version
- memory data

The storage contract will be defined separately from this memory contract.

## Validation

The memory implementation must reject malformed memory data.

Validation must cover at least:

- missing id
- missing memory type
- invalid memory type
- missing content
- invalid provenance
- invalid lifecycle state
- invalid sensitivity
- malformed timestamps

## Architecture Independence

The Memory contract must not depend on:

- PostgreSQL
- SQLite
- vector databases
- embeddings
- a particular LLM
- a particular cloud provider
- a particular connector

These technologies may be introduced in later phases without changing the semantic meaning of Memory.

## Version

Contract version: 1
