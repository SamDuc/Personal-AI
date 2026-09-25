# Local Retrieval Contract

## 1. Purpose

This contract defines the boundary between indexed local content and the
retrieval layer.

Retrieval operates on indexed representations and returns resources that
are eligible for retrieval under the existing source, searchability, and
access policy.

This contract does not define embeddings, vector storage, ranking,
full-text search implementation, LLM processing, or agent behavior.

## 2. Source Identity

The initial retrieval source is `local_filesystem`.

The original filesystem resource remains authoritative.

The local index is a derived representation.

## 3. Input

Retrieval accepts canonical `DataItem` records representing indexed
resources.

A retrievable local item MUST satisfy all of the following:

- `source` is `local_filesystem`;
- `searchable` is `true`;
- `content_available` is `true`;
- `content_ref` is present;
- `access_policy.read` is `true`.

Retrieval MUST NOT grant or modify permissions.

## 4. Retrieval Request

A retrieval request contains:

- a query string;
- an optional source restriction;
- a maximum result count.

The query is passed to the retrieval implementation.

The contract does not prescribe how the query is matched against indexed
content.

## 5. Retrieval Result

A retrieval result identifies a canonical `DataItem`.

The result MUST preserve the item's:

- `id`;
- `source`;
- `source_id`;
- `uri`;
- `content_ref`;
- `content_hash`;
- `sensitivity`.

Retrieval results MUST retain enough information to locate the original
source resource.

## 6. Searchability

`searchable` indicates that the item is available to retrieval systems.

`searchable` alone does not grant read permission.

An item without readable access MUST NOT be returned as an authorized
retrieval result.

## 7. Permissions

The existing access policy remains authoritative.

Retrieval MUST NOT:

- change `access_policy`;
- elevate permissions;
- bypass deny-by-default behavior;
- expose an item whose `access_policy.read` is false.

Permission configuration remains outside the retrieval implementation.

## 8. Sensitivity

Sensitivity remains part of the canonical `DataItem`.

Retrieval does not change sensitivity classification.

Credentials, private keys, tokens, and similar secrets remain outside
ordinary searchable knowledge according to the unified data model.

## 9. Source Authority

Retrieval does not modify the original source.

It MUST NOT:

- modify;
- rename;
- move;
- delete;
- execute;
- upload;
- share

the original source resource.

## 10. Scope

The initial implementation is local-only.

It MUST NOT recursively discover files.

It MUST operate only on `DataItem` records explicitly supplied to it.

## 11. Ranking and Search Backend Boundary

This contract does not define:

- lexical search;
- semantic search;
- embeddings;
- vector databases;
- ranking algorithms;
- scoring;
- chunking;
- top-k ranking semantics.

These may be introduced by later contracts or implementations.

## 12. Separation of Responsibilities

Retrieval is independent from:

- filesystem discovery;
- content extraction;
- content indexing;
- embedding generation;
- vector storage;
- LLM providers;
- cloud connectors;
- email connectors;
- agent actions.

## 13. Contract Version

Contract version: 1.
