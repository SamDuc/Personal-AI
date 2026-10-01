# Canonical DataItem Retrieval Boundary

## 1. Purpose

This contract defines the canonical resource boundary between
File Intelligence retrieval and higher-level consumers.

## 2. Canonical Resource

`DataItem` remains the canonical resource identity.

No additional File Intelligence resource identity is introduced.

## 3. Retrieval Result

A retrieval result returns a canonical `DataItem`.

The result MUST preserve the canonical identity and source information.

## 4. Eligibility

A local filesystem DataItem is retrieval-eligible only when:

- `source == "local_filesystem"`;
- `searchable == true`;
- `content_available == true`;
- `content_ref` is present;
- `sync_status == "indexed"`;
- `access_policy.read == true`.

## 5. Consistency

Retrieval MUST NOT expose an indexed representation as current when
the consistency boundary determines that it is not eligible.

The consistency states remain defined by the existing source/index
consistency contract.

## 6. Authorization

Retrieval MUST NOT grant, elevate, or bypass permissions.

`DataItem.access_policy` remains authoritative.

## 7. Consumer Boundary

Higher-level consumers MUST depend on the canonical `DataItem`,
`RetrievalRequest`, and `RetrievalResult` contracts rather than
File Intelligence implementation details.

Consumers MUST NOT require knowledge of:

- filesystem discovery;
- capability resolution;
- authorization implementation;
- extraction implementation;
- normalization implementation;
- content index implementation;
- consistency implementation.

## 8. Separation

This contract does not define:

- extraction;
- indexing implementation;
- ranking;
- embeddings;
- vector storage;
- LLM processing;
- provider routing;
- automatic refresh;
- filesystem watching;
- cloud connectors;
- email connectors;
- agent actions.

## 9. Compatibility

Existing `DataItem`, `ContentIndex`, local retrieval, and source/index
consistency contracts remain authoritative.

## 10. Contract Version

Version: 1
