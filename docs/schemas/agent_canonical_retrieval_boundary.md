# Agent ↔ Canonical Retrieval Boundary

## 1. Purpose

This contract defines the boundary through which the Agent requests
retrieval of authorized personal-data resources.

## 2. Retrieval Ownership

Retrieval remains a separate capability.

The Agent MUST coordinate retrieval through a supplied retrieval
capability.

The Agent MUST NOT implement retrieval internally.

## 3. Request Boundary

A retrieval request MUST use the existing `RetrievalRequest` contract.

The request contains:

- query;
- optional source restriction;
- maximum result count.

The Agent MUST preserve the user's retrieval intent when constructing
the retrieval request.

## 4. Result Boundary

Retrieval MUST return the existing `RetrievalResult` representation.

Each result identifies the canonical `DataItem`.

The Agent MUST NOT replace `DataItem` with a new resource model.

## 5. Agent Restrictions

The Agent MUST NOT:

- access local files directly;
- access `ContentIndex` directly;
- perform filesystem discovery;
- perform content extraction;
- implement lexical search;
- implement semantic search;
- perform ranking;
- generate embeddings;
- bypass retrieval permissions.

## 6. Permission Boundary

Retrieval permissions remain authoritative.

The Agent MUST NOT:

- grant permissions;
- modify `access_policy`;
- bypass deny-by-default behavior;
- expose unreadable resources.

## 7. Source Boundary

The original source remains authoritative.

Agent retrieval coordination MUST NOT:

- modify;
- rename;
- move;
- delete;
- execute;
- upload;
- share

the source resource.

## 8. Capability Independence

The Agent MUST remain independent from:

- filesystem implementation;
- ContentIndex implementation;
- lexical search implementation;
- semantic search implementation;
- vector database;
- embedding implementation;
- specific LLM provider.

## 9. Failure

Retrieval capability failures MUST propagate to the Agent.

The Agent MUST NOT:

- fabricate retrieval results;
- silently ignore retrieval failures;
- bypass retrieval by directly accessing personal data;
- automatically substitute another retrieval implementation;
- retry or fallback as part of this boundary.

## 10. Scope

The initial implementation remains local-only.

Retrieval MUST operate only on explicitly supplied canonical `DataItem`
records.

No recursive discovery is introduced by this contract.

## 11. Compatibility

The existing canonical retrieval contract remains authoritative.

The existing Agent contract remains authoritative.

This contract does not redefine `RetrievalRequest`, `RetrievalResult`,
or `DataItem`.

## 12. Contract Version

Version: 1
