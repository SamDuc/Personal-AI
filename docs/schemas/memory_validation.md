# Memory Validation Contract

## Purpose

Define the domain validation rules for a canonical Memory object.

Validation operates on a `Memory` object and is independent of JSON
persistence, databases, vector stores, embeddings, LLMs, connectors,
retrieval, and permission execution.

## Validation Scope

The validator must verify:

- identity
- memory type
- content
- provenance
- timestamps
- lifecycle status
- sensitivity
- metadata structure

The validator must not:

- modify the Memory object
- modify authoritative source data
- grant permissions
- perform external actions
- infer user attributes
- upgrade confidence
- change lifecycle state
- persist data

## Validation Matrix

| Field | Required | Valid Representation | Reject |
|---|---|---|---|
| id | Yes | non-empty string | missing, empty, non-string |
| memory_type | Yes | MemoryType | missing, invalid type |
| content | Yes | string | missing, non-string |
| provenance | Yes | MemoryProvenance | missing, invalid structure |
| provenance.source | Yes | MemorySource | invalid source |
| provenance.source_ref | Yes | string | non-string |
| provenance.method | Yes | MemoryProvenanceMethod | invalid method |
| provenance.confidence | Yes | MemoryConfidence | invalid confidence |
| provenance.recorded_at | Yes | datetime | missing, invalid timestamp |
| created_at | No | datetime or None | invalid type |
| updated_at | No | datetime or None | invalid type |
| expires_at | No | datetime or None | invalid type |
| status | Yes | MemoryLifecycleStatus | invalid lifecycle state |
| sensitivity | Yes | normal/private/sensitive/restricted | invalid value |
| metadata | No | MemoryMetadata or None | invalid structure |

## Required Domain Rules

### Identity

`id` must be a non-empty string.

### Memory Type

`memory_type` must be one of the defined MemoryType values:

- semantic
- episodic
- working
- procedural

### Content

`content` must be a string.

### Provenance

Every Memory must contain valid provenance.

The provenance source must be one of:

- user
- trusted_system
- external_source

The provenance method must be one of:

- explicit
- imported
- derived

The provenance confidence must be one of:

- explicit
- high
- medium
- low

`source_ref` must be a string.

`recorded_at` must be a valid datetime.

Derived or inferred information must not be treated as explicit user-provided information.

### Timestamps

`created_at` and `updated_at` may be absent (`None`) because the current
Memory model permits optional values.

When present, they must be datetime values.

`expires_at` is optional and may be `None`.

Datetime timezone preservation is a persistence concern; domain validation
must reject invalid non-datetime values but must not invent timezone data.

### Lifecycle

`status` must be one of:

- candidate
- active
- superseded
- archived
- expired

Validation must not perform lifecycle transitions.

### Sensitivity

`sensitivity` must be one of:

- normal
- private
- sensitive
- restricted

The validator must not infer sensitivity from content.

### Metadata

Metadata is auxiliary information.

When present, it must be a `MemoryMetadata` instance.

Metadata must not override canonical Memory fields or provenance.

## Error Behavior

Invalid Memory data must be rejected.

The validator should raise a clear validation exception identifying
the invalid field or rule.

Validation errors must not silently repair or normalize invalid data.

## Architecture Independence

The validator must not depend on:

- PostgreSQL
- SQLite
- vector databases
- embeddings
- a particular LLM
- cloud providers
- connectors
- retrieval systems
- permission execution

## Contract Version

Validation contract version: 1

## Validation API

### Primary Function

```python
validate_memory(memory: Memory) -> None
```

A valid `Memory` object causes the function to return `None`.

Invalid memory data causes `MemoryValidationError` to be raised.

### Exception

```python
class MemoryValidationError(ValueError):
    """Raised when a Memory violates the validation contract."""
```

### API Boundary

The validator accepts a canonical `Memory` object.

The validator does not:

- serialize Memory
- deserialize JSON
- persist Memory
- retrieve Memory
- modify Memory
- modify source data
- perform lifecycle transitions
- perform permission checks
- perform external actions

### Mutation

`validate_memory()` must not mutate the supplied Memory object.

### Type Boundary

JSON and dictionary parsing remain the responsibility of the persistence layer.

### Contract Version

Validation API version: 1
