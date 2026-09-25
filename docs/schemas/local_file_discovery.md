# Local Filesystem Discovery Contract

## 1. Purpose

The local filesystem discovery layer enumerates files within an explicitly authorized filesystem scope and collects filesystem metadata.

Its responsibility is limited to discovery and metadata collection.

Discovery produces `LocalFileMetadata` records that can later be mapped to the canonical `DataItem` model.

This contract does not define content extraction, indexing, embeddings, vector storage, retrieval, or LLM processing.

---

## 2. Source Identity

The discovery source is identified as:

    local_filesystem

The source configuration is defined in:

    config/sources/sources.yaml

The caller or orchestration layer MUST ensure that
`sources.local_filesystem.enabled` is true before invoking discovery.

The discovery function itself does not load or interpret
`config/sources/sources.yaml`.

When the source is disabled, the caller or orchestration layer
must not invoke discovery.

---

## 3. Scope

Every discovery operation MUST receive an explicit filesystem scope.

The discovery layer MUST NOT:

- invent a default filesystem root;
- scan the entire filesystem by default;
- scan all available drives by default;
- expand the requested scope silently;
- inspect paths outside the requested scope.

A missing or invalid scope must not result in an unrestricted scan.

The scope is supplied by the caller and represents the boundary within which discovery is permitted.

---

## 4. Discovery API

The discovery layer exposes a function conceptually equivalent to:

    discover_local_files(scope: Path) -> list[LocalFileMetadata]

The exact implementation may use an internal result or error model later, but the public behavior must follow this contract.

---

## 5. Scope Validation

Before enumeration, the discovery layer MUST validate the supplied scope.

### 5.1 Scope does not exist

If the scope does not exist, discovery must fail explicitly.

It must not silently treat the missing path as an empty directory.

### 5.2 Scope is not a directory

If the supplied scope identifies a regular file rather than a directory, discovery must fail explicitly.

The discovery operation is directory-scoped.

### 5.3 Scope is inaccessible

If the scope cannot be accessed because of filesystem permissions or availability, discovery must report the failure.

It must not represent the inaccessible scope as successfully scanned.

---

## 6. Enumeration

Discovery enumerates files within the authorized scope.

Directories are traversal containers and are not emitted as ordinary file `LocalFileMetadata` records.

The initial discovery contract supports recursive enumeration within the explicit scope.

The implementation MUST NOT escape the authorized scope during recursion.

---

## 7. File Metadata

For every successfully discovered file, the discovery layer should collect:

- `path`
- `size`
- `created_at`, when available
- `modified_at`, when available
- `mime_type`, when determinable

The metadata record is represented by `LocalFileMetadata`.

The path identifies the native filesystem resource.

---

## 8. Content Access Boundary

Discovery MUST NOT read the full contents of every discovered file.

Discovery is metadata-only.

Therefore discovery must not perform:

- PDF text extraction;
- document parsing;
- OCR;
- image decoding for content analysis;
- audio/video decoding;
- archive extraction;
- source-code analysis;
- embedding generation;
- LLM processing.

A discovered file may therefore produce metadata even when its content is not available.

---

## 9. DataItem Mapping

Discovery metadata may be converted into the canonical `DataItem` through the local filesystem mapper:

    LocalFileMetadata
        -> local_file_to_data_item()
        -> DataItem

The mapper is responsible for canonical identity and metadata representation.

Discovery itself does not perform indexing or retrieval.

---

## 10. Permissions

Filesystem discovery must respect the permission architecture defined by:

    config/permissions/permissions.yaml

The system uses deny-by-default permissions.

Discovery MUST NOT grant effective read or write permission to a `DataItem`.

In particular, discovery must not change `DataItem.access_policy.read` from its deny-by-default state.

Source capability and effective permission are separate concerns.

The local filesystem source may be configured with `access_mode: read_only` but this does not itself grant Personal AI permission to access a resource.

---

## 11. Read-Only Behavior

The discovery layer is read-only.

It MUST NOT:

- create files;
- modify files;
- rename files;
- move files;
- delete files;
- change filesystem permissions;
- execute discovered files;
- upload files;
- share files.

Discovery only observes filesystem metadata.

---

## 12. Error Handling

Discovery should distinguish at least the following situations:

- scope does not exist;
- scope is not a directory;
- permission denied;
- filesystem resource unavailable;
- metadata unavailable;
- individual file discovery failure.

A failure to inspect one resource must not be represented as successful metadata for that resource.

Where practical, discovery should continue with other accessible files when an individual file cannot be inspected.

The exact error/result aggregation mechanism may be defined by a later contract.

---

## 13. Determinism

Given the same filesystem state and the same authorized scope, discovery should produce equivalent metadata records.

The discovery layer should avoid introducing nondeterministic transformations into filesystem identity.

Filesystem-native paths remain authoritative.

---

## 14. Separation of Responsibilities

The discovery layer is independent from:

- databases;
- vector databases;
- embedding models;
- LLMs;
- retrieval engines;
- cloud connectors;
- email connectors;
- content extraction pipelines.

The discovery layer only produces filesystem metadata.

---

## 15. Security Boundaries

The discovery layer MUST treat filesystem scope as an explicit security boundary.

It must not:

- follow a path outside the authorized scope;
- silently broaden scope;
- expose file contents;
- bypass permission checks;
- execute filesystem resources.

Sensitive files may be discovered as metadata, but discovery does not automatically make their contents searchable or accessible.

---

## 16. Contract Version

Version: 1

This contract defines local filesystem discovery behavior independently from the implementation.

Changes to scope semantics, enumeration behavior, metadata requirements, permissions, or content access boundaries require an explicit contract revision.
