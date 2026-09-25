# Local Filesystem Source Contract

## Purpose

Define the contract for reading local filesystem resources and representing them as canonical `DataItem` objects.

This contract governs local filesystem discovery only.

It does not define content extraction, embeddings, vector storage, LLM processing, retrieval ranking, or cloud connectors.

## Source Identity

The source identifier is:

``text
local_filesystem
``

The source is configured through:

``text
config/sources/sources.yaml
``

## Enablement

A local filesystem scan may run only when:

``text
sources.local_filesystem.enabled == true
``

When the source is disabled, the connector must not scan or inspect local filesystem resources.

## Access Mode

The current supported access mode is:

``text
read_only
``

The connector may:

- enumerate files within an explicitly authorized scope;
- read filesystem metadata;
- determine file type information when available;
- construct `DataItem` representations.

The connector must not:

- create files;
- modify files;
- rename files;
- move files;
- delete files;
- change permissions;
- execute discovered files;
- upload or share discovered files.

## Scope

Filesystem discovery must operate only on an explicitly supplied scope.

The connector must not:

- scan the entire filesystem by default;
- invent a scan root;
- silently expand the configured scope;
- follow a path outside the authorized scope.

If no valid scope is supplied, discovery must not start.

## Discovery

For each discovered filesystem resource, the connector should collect metadata available from the operating system, including:

- name;
- path;
- file size;
- creation time when available;
- modification time when available;
- file extension when applicable;
- MIME type when available.

Directories may be discovered for traversal but are not represented as ordinary file `DataItem` resources unless a later contract explicitly defines directory items.

## DataItem Mapping

A discovered local file maps to the canonical `DataItem` model.

| DataItem field | Local filesystem representation |
| --- | --- |
| `id` | Stable Personal AI identifier |
| `source` | `local_filesystem` |
| `source_id` | Native local filesystem path |
| `uri` | Canonical file URI |
| `item_type` | `file` |
| `mime_type` | Detected MIME type when available |
| `extension` | File extension when applicable |
| `name` | File name |
| `size` | File size in bytes |
| `created_at` | Filesystem creation time when available |
| `modified_at` | Filesystem modification time when available |
| `content_available` | Whether searchable content has been extracted |
| `content_ref` | Reference to extracted content when available |
| `content_hash` | Content hash when available |
| `project` | Project association when known |
| `topics` | Topics when assigned or inferred |
| `tags` | Tags when assigned |
| `searchable` | Whether available to retrieval systems |
| `embedding_ref` | Embedding reference when available |
| `indexed_at` | Time the resource was indexed |
| `source_modified_at` | Last known filesystem modification time |
| `sync_status` | Current indexing/synchronization state |
| `access_policy` | Applicable access policy |
| `sensitivity` | Applicable sensitivity classification |

The canonical `DataItem` model remains authoritative for the normalized representation.

## Source Authority

The local filesystem remains authoritative for the original file.

The `DataItem` must represent the source through metadata and references rather than becoming an independent authoritative copy.

Changing or deleting a `DataItem` must not be interpreted as changing the original filesystem resource.

## Content Handling

Filesystem discovery and content extraction are separate operations.

The discovery stage must not automatically read the full contents of every discovered file.

A file may have:

``text
content_available = false
``

when searchable content has not been extracted.

Content extraction may be introduced by a later contract.

## Error Handling

Filesystem errors must not cause the entire discovery operation to fail unnecessarily.

The connector should distinguish conditions such as:

- path does not exist;
- permission denied;
- file unavailable;
- unsupported filesystem metadata;
- transient filesystem error.

An inaccessible resource must not be represented as successfully read merely because its path was discovered.

## Security

Credentials, private keys, tokens, secrets, and similar sensitive resources must not automatically become ordinary searchable knowledge.

Sensitivity and access policy must remain explicit in the `DataItem`.

Filesystem discovery does not grant additional permissions.

## Determinism

Given the same accessible filesystem state and the same authorized scope, discovery should produce deterministic source identity and metadata representation where the underlying filesystem metadata is stable.

## Independence

The local filesystem source contract must remain independent of:

- database implementation;
- vector database implementation;
- embedding provider;
- LLM provider;
- retrieval ranking implementation;
- cloud storage connectors;
- email connectors.

## Contract Version

This contract is version 1.

Changes that alter source identity, access semantics, scope rules, or canonical `DataItem` mapping require an explicit contract update.
