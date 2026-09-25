# Local Content Index Contract

## 1. Purpose

This contract defines the local index representation of derived content extracted from an explicitly selected local file.

The local content index provides metadata and permitted searchable representations for later retrieval.

The original local filesystem file remains authoritative.

This contract does not define embeddings, vector storage, retrieval ranking, LLM processing, cloud connectors, or agent behavior.

## 2. Source Identity

The source identity is `local_filesystem`.

The original source file remains at its filesystem location whenever possible.

Indexed content is a derived representation and must not replace the source file.

## 3. Input

The index accepts content produced by the local file content extraction contract.

The extracted content must identify:

- the source file path;
- extracted text;
- content hash;
- content availability;
- extraction version.

The index MUST NOT perform filesystem discovery or content extraction implicitly.

## 4. Index Reference

An indexed content representation MUST expose a `content_ref`.

The reference identifies the derived indexed content.

The reference uses the `index://content/...` URI form.

The exact identifier generation strategy is an implementation detail unless a later contract requires interoperability.

## 5. Content Hash

The index MUST preserve the content hash produced by extraction.

The hash represents extracted content rather than filesystem metadata.

The index MUST NOT silently replace the extracted content hash with a hash of unrelated metadata.

## 6. DataItem Integration

An indexed local file may populate the canonical `DataItem` fields:

- `content_available`;
- `content_ref`;
- `content_hash`;
- `searchable`;
- `indexed_at`;
- `source_modified_at`;
- `sync_status`.

When indexed content is available:

- `content_available` MUST be `true`;
- `content_ref` MUST identify the indexed content;
- `content_hash` MUST be present;
- `searchable` MUST be `true`;
- `indexed_at` MUST identify when indexing occurred;
- `sync_status` MUST be `indexed`.

## 7. Embedding Boundary

The local content index does not generate embeddings.

`embedding_ref` MUST remain unset unless a separate embedding/indexing contract is introduced.

Embedding generation is outside this contract.

## 8. Source Authority

The local filesystem remains authoritative for the original file.

The local content index is a derived representation.

Changes to the source file may require the indexed representation to be refreshed by later synchronization logic.

The index MUST NOT modify the original source file.

## 9. File Access Boundary

Indexing operates only on explicitly provided extracted content.

It MUST NOT recursively scan directories.

It MUST NOT access unrelated files.

It MUST NOT modify, rename, move, delete, execute, upload, or share source files.

## 10. Searchability

An item MUST NOT be marked searchable merely because filesystem metadata exists.

An item may be marked searchable only when permitted extracted content has been successfully represented by the local content index.

Searchability does not imply permission to modify or externally share the source.

## 11. Permissions and Sensitivity

Indexing does not grant permissions.

Existing access policy and sensitivity information remain authoritative.

Sensitive content must not automatically become ordinary unrestricted knowledge merely because it has been indexed.

The permission layer remains responsible for authorization.

## 12. Determinism

Given the same extracted content and the same contract version, indexing should preserve the same content hash.

The original filesystem path remains authoritative for source identity.

## 13. Separation of Responsibilities

This contract is independent from:

- filesystem discovery;
- content extraction;
- database storage;
- vector storage;
- embedding generation;
- retrieval ranking;
- LLM processing;
- cloud connectors;
- email connectors;
- agent actions.

The local content index only represents permitted extracted local content for later retrieval.

## 14. Contract Version

Contract version: 1.
