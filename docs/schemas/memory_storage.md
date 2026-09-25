# Memory Storage Contract

## Purpose

Define the canonical JSON persistence contract for the Memory layer.

The storage format must preserve the semantic meaning of the Memory contract without depending on a database, vector store, embedding provider, LLM provider, or retrieval implementation.

## Storage Format

The canonical persistence format is JSON.

The storage document must contain:

- version
- memory

## Version

The initial storage contract version is:

- 1

Unknown storage versions must be rejected.

## Memory Fields

The persisted memory object must preserve:

- id
- memory_type
- content
- provenance
- created_at
- updated_at
- expires_at
- status
- sensitivity
- metadata

## Provenance Fields

The persisted provenance object must preserve:

- source
- source_ref
- method
- confidence
- recorded_at

## Datetime Representation

Datetime values must be serialized as timezone-aware ISO 8601 strings when timezone information is available.

Optional `expires_at` may be represented as `null`.

## Enum Representation

Enum values must be persisted using their string values.

The storage format must not depend on Python enum implementation details.

## Metadata

Metadata may be persisted when present.

Metadata must not override canonical Memory fields or provenance.

## Validation

Storage loading must reject malformed data.

Validation must cover at least:

- missing version
- unsupported version
- missing memory
- missing id
- missing memory type
- invalid memory type
- missing content
- invalid provenance
- invalid lifecycle state
- invalid sensitivity
- malformed timestamps

## Round Trip

A valid Memory object must be serializable to the canonical JSON representation and reconstructable without loss of semantic information.

Round-trip persistence must preserve:

- identity
- memory type
- content
- provenance
- timestamps
- lifecycle status
- sensitivity
- metadata

## Source Authority

Persistence stores the memory representation only.

It must not replace or modify the authoritative source referenced by the memory provenance.

## Security

The persistence layer must not:

- grant permissions
- perform external actions
- treat credentials as ordinary memory
- introduce authentication state

## Architecture Independence

The storage contract must not depend on:

- PostgreSQL
- SQLite
- vector databases
- embeddings
- a particular LLM
- a particular cloud provider
- a particular connector

## Contract Version

Storage contract version: 1
