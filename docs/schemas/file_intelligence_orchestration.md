# File Intelligence Orchestration Contract

## 1. Purpose

This contract defines the orchestration boundary for the local file
intelligence pipeline.

The orchestration layer composes existing file-intelligence boundaries
without redefining their individual responsibilities.

## 2. Pipeline

The intended pipeline is:

Authorized Scope
-> Discovery
-> Capability Resolution
-> Authorization Gate
-> Extractor Registry
-> Extraction
-> Normalization
-> Canonical DataItem
-> Content Index

Retrieval remains a separate downstream operation over indexed DataItems.

## 3. Responsibilities

The orchestration layer MAY:

- coordinate the existing discovery boundary;
- resolve file capability;
- enforce authorization before content extraction;
- resolve an extractor through the extractor registry;
- invoke extraction for an authorized supported file;
- normalize extracted content;
- connect normalized content to the canonical DataItem;
- index permitted normalized content.

The orchestration layer MUST NOT:

- redefine filesystem scope semantics;
- grant permissions;
- bypass PermissionEvaluator;
- perform filesystem-wide discovery;
- implement file-type extraction itself;
- generate embeddings;
- perform semantic analysis;
- perform LLM processing;
- perform retrieval ranking;
- modify source files;
- upload or share source files.

## 4. Authorization Order

Authorization MUST occur before content extraction.

The required order is:

Permission / Authorization
-> Filesystem Scope
-> Discovery / File Selection
-> Capability Resolution
-> Extraction

An unsupported capability MUST stop before extraction.

An unauthorized file MUST stop before extraction.

## 5. Source Authority

The local filesystem remains authoritative.

All extracted, normalized, indexed, and DataItem representations are
derived representations.

The orchestration layer MUST NOT modify the original source file.

## 6. DataItem Boundary

The canonical DataItem remains the normalized representation of the
discovered local resource.

Indexing may populate:

- content_available;
- content_ref;
- content_hash;
- searchable;
- indexed_at;
- source_modified_at;
- sync_status.

The orchestration layer MUST NOT fabricate embedding_ref.

## 7. Error Boundary

An orchestration failure MUST identify the failed stage.

The orchestration layer MUST NOT silently continue after:

- authorization failure;
- unsupported capability;
- missing extractor;
- extraction failure;
- normalization failure;
- indexing failure.

It MUST NOT broaden scope or authorization as a recovery mechanism.

## 8. Retrieval Separation

Retrieval is downstream from indexing.

The orchestration layer MUST NOT silently perform retrieval ranking or
semantic search.

A separate retrieval request remains responsible for retrieval.

## 9. Contract Version

Contract version: 1.
