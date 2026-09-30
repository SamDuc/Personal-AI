# Canonical DataItem / Content Index Integration Contract

Version: 1

## Purpose

Define the integration boundary between normalized file content,
the canonical DataItem representation, and the ContentIndex.

## Processing

DataItem
-> normalized content
-> ContentIndex
-> indexed DataItem state

## DataItem

The existing DataItem remains the canonical resource identity.

Integration MUST preserve:

- id
- source
- source_id
- uri
- item_type
- mime_type
- extension
- name
- size
- access_policy
- sensitivity

## Source Matching

The normalized content source path MUST identify the same local
filesystem resource as DataItem.source_id.

A source mismatch MUST fail before index integration.

## Index Integration

Successful ContentIndex indexing MUST populate:

- content_available = true
- content_ref
- content_hash
- searchable = true
- indexed_at
- sync_status = "indexed"

The content hash MUST be preserved from NormalizedContent.

## Permissions

Integration MUST NOT:

- grant permissions;
- change access_policy;
- bypass authorization;
- change sensitivity.

## Embeddings

Integration MUST NOT create or modify embedding_ref.

## Source Authority

The filesystem remains authoritative.

Integration MUST NOT modify, rename, move, delete, execute, upload,
or share the source file.

## Separation

Integration MUST NOT perform:

- discovery;
- capability resolution;
- authorization;
- extraction;
- normalization;
- retrieval;
- embeddings;
- vector search;
- LLM processing;
- provider routing;
- fallback;
- retry.

## Error Boundary

The integration MUST distinguish source mismatch and invalid index
inputs from upstream extraction/normalization failures.

## Determinism

The same normalized content and index contract MUST preserve the same
content hash.

## Compatibility

Existing DataItem and ContentIndex contracts remain authoritative.

## Contract Version

1
