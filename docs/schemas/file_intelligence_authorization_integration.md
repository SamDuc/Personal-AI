# File Intelligence Authorization Integration Contract

Version: 1

## Purpose

Integrate the B-07-02 authorization decision boundary
into the B-07-01 file intelligence orchestration boundary.

## Required Processing Order

Capability Resolution
-> Authorization Gate
-> Extractor Resolution
-> Extraction
-> Normalization

## Authorization

- The authorization gate MUST execute before extraction.
- A denied authorization decision MUST stop processing.
- `confirmation_required` MUST NOT be treated as authorized.
- Filesystem scope MUST be enforced.
- Permission evaluation remains authoritative.
- The orchestrator MUST NOT grant permissions.

## Capability

- Capability resolution remains a separate boundary.
- Unsupported capability MUST remain distinguishable.
- Unsupported capability MUST NOT reach an extractor.

## Extractor

- An extractor MUST NOT execute after authorization denial.
- The orchestrator MUST NOT implement extraction itself.
- Extractor selection remains the responsibility of the extractor registry.

## Normalization

- Normalization occurs only after successful extraction.
- Existing normalization behavior remains unchanged.

## Separation of Responsibilities

This integration MUST NOT introduce:

- content indexing
- retrieval
- embeddings
- vector search
- sensitivity classification
- LLM document processing
- permission granting
- permission policy mutation
- provider routing
- fallback
- retry
- cross-provider orchestration

## Error Boundary

Authorization failures MUST remain distinguishable from:

- unsupported capability
- missing extractor
- extraction failure
- normalization failure

## Compatibility

Existing B-07-01 orchestration behavior MUST remain valid for
authorized and supported files.

## Version

1
