# Local File Content Extraction Contract

## 1. Purpose

This contract defines content extraction from an explicitly selected local file.

Content extraction is separate from filesystem discovery. Discovery produces filesystem metadata; extraction reads file content only when explicitly requested by the caller or orchestration layer.

This contract does not define embeddings, vector storage, retrieval ranking, LLM processing, project/topic inference, or cloud connectors.

## 2. Source Identity

The source identity is `local_filesystem`.

The local filesystem remains authoritative for the original file.

Extracted content is a derived representation and must not be treated as an authoritative replacement for the source file.

## 3. Scope

Every extraction operation MUST receive an explicit file path.

The extraction operation MUST NOT silently broaden the request to other files, directories, drives, or the whole filesystem.

The caller or orchestration layer is responsible for ensuring that the source is enabled and that the requested file is within an authorized scope before extraction is invoked.

The extraction function itself does not load or interpret `config/sources/sources.yaml`.

## 4. Supported Content

Version 1 supports plain-text files that can be decoded using an explicitly defined text encoding strategy.

The implementation MUST NOT claim support for a file type unless it can extract its content according to this contract.

PDF parsing, office-document parsing, OCR, image analysis, audio/video decoding, archive extraction, and source-code semantic analysis are outside the scope of version 1.

## 5. Extraction API

The conceptual API is:

    extract_local_file_content(path: Path) -> ExtractedContent

The result represents extracted content and metadata about the extraction operation.

## 6. Content Representation

An extracted content result MUST contain:

- the source file path;
- the extracted text content;
- a content hash;
- an indication that content is available;
- information sufficient to identify the extraction format/version.

The extracted text is derived content. The original file remains authoritative.

## 7. Content Hash

The extractor MUST calculate a deterministic hash for the extracted content.

The hash represents the extracted content, not filesystem metadata.

The same extracted content under the same extraction contract MUST produce the same hash.

The hash may be used by later indexing or synchronization logic for change detection and deduplication.

The specific hash algorithm is an implementation detail unless a later contract requires interoperability.

## 8. DataItem Boundary

Extraction may provide the values required to populate:

- `content_available`;
- `content_ref`;
- `content_hash`;
- `searchable`.

Extraction MUST NOT generate `embedding_ref`.

Extraction MUST NOT perform retrieval indexing or embedding generation.

`content_ref` identifies derived extracted content; its storage mechanism is outside this contract.

## 9. File Access Boundary

Extraction reads the explicitly requested source file.

It MUST NOT modify, rename, move, delete, execute, upload, or share the source file.

Extraction MUST NOT recursively scan unrelated files.

## 10. Encoding

Version 1 MUST use an explicit and deterministic text decoding strategy.

A decoding failure MUST be reported as an extraction error rather than silently producing corrupted text.

The implementation MUST NOT silently replace undecodable content in a way that changes the extracted meaning.

## 11. Error Handling

The implementation MUST distinguish, where practical, at least:

- missing source file;
- source path is not a regular file;
- permission/access failure;
- unsupported content type;
- decoding failure;
- extraction/read failure.

Errors must not cause unrelated files to be scanned or exposed.

## 12. Security and Sensitivity

Extraction does not grant permissions.

Existing access policy and sensitivity information remain authoritative.

Sensitive files may only be extracted when the caller has already authorized the required access.

Credentials, private keys, tokens, secrets, and similar sensitive resources must not automatically become ordinary searchable knowledge.

## 13. Determinism

Given the same source content and the same extraction contract/version, extraction should produce the same text and content hash.

The source file path remains filesystem-native and authoritative.

## 14. Separation of Responsibilities

This contract is independent from:

- filesystem discovery;
- database storage;
- vector storage;
- embedding generation;
- retrieval ranking;
- LLM processing;
- cloud connectors;
- email connectors.

Content extraction only transforms an explicitly selected local file into derived searchable content.

## 15. Contract Version

Contract version: 1.
