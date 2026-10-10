# File Intelligence Authorization Contract

Version: 1

## Purpose

Define the authorization gate between file capability resolution
and content extraction.

## Required Authorization Order

1. Explicit filesystem scope
2. Source enabled
3. Read permission
4. Capability resolution
5. Authorization gate
6. Extraction

## Filesystem Boundary

A file outside `FilesystemAccessScope` MUST NOT be processed.

The authorization gate MUST NOT broaden the authorized filesystem scope.

## Permission Boundary

The gate MUST use `PermissionEvaluator`.

A denied read permission MUST prevent extraction.

`confirmation_required` MUST NOT be treated as allowed.

The authorization gate MUST NOT grant permissions.

## Capability Boundary

Unsupported file capability MUST NOT reach an extractor.

Capability resolution remains separate from extraction.

## DataItem Boundary

Authorization MUST NOT grant write permission.

Authorization MUST NOT mutate unrelated access policy.

## Sensitivity

Sensitivity is metadata only in version 1.

The authorization gate MUST NOT infer, classify, or escalate sensitivity.

No sensitivity classifier is introduced by this contract.

## Source Authority

The local filesystem remains authoritative.

The authorization gate MUST NOT modify source files.

## Retrieval Boundary

Authorization does not perform retrieval, ranking, search,
embedding, or indexing.

Retrieval remains a downstream boundary.

## Error Boundary

Authorization failure MUST prevent downstream extraction.

The gate MUST distinguish authorization denial from unsupported
capability.

The gate MUST NOT silently bypass authorization failures.

## Security

The gate MUST NOT:

- broaden filesystem scope
- bypass `PermissionEvaluator`
- grant permissions
- expose unauthorized file content
- convert `confirmation_required` into `allowed`

## Prohibited Scope

Version 1 does not introduce:

- extraction implementation
- OCR
- PDF/DOCX parsing
- embeddings
- vector search
- RAG
- LLM classification
- permission escalation
- automatic sensitivity classification
- provider routing
- fallback or retry behavior
- cross-provider orchestration
