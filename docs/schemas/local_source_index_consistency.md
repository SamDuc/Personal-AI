# Local Source/Index Consistency Contract

## 1. Purpose

This contract defines consistency semantics between the authoritative local
filesystem source and its derived indexed content representation.

The filesystem remains authoritative.

The index is a derived representation.

This contract does not define extraction, indexing implementation,
retrieval ranking, embeddings, vector storage, background synchronization,
or filesystem watching.

---

## 2. Source Identity

The authoritative source is identified by:

    local_filesystem

The canonical filesystem identity is the resolved source path represented
by `DataItem.source_id` and the corresponding indexed source path.

The index MUST NOT replace the filesystem source identity with an unrelated
derived identifier.

---

## 3. Source Snapshot

A source snapshot records the filesystem metadata observed for the source
representation associated with indexed content.

The relevant source modification timestamp is:

    source_modified_at

The timestamp represents the source metadata snapshot associated with the
indexed representation.

It MUST NOT be interpreted as the time at which the index operation occurred.

---

## 4. Index Timestamp

The timestamp:

    indexed_at

identifies when the derived indexed representation was created or refreshed.

It MUST NOT be used as a substitute for the source modification timestamp.

---

## 5. Content Hash

The indexed content hash:

    content_hash

MUST represent the extracted content associated with the indexed
representation.

It MUST NOT be replaced by a filesystem metadata hash or an unrelated
source metadata value.

---

## 6. Consistency States

The consistency boundary recognizes these states:

- `consistent`
- `out_of_sync`
- `source_missing`
- `source_unavailable`

### 6.1 consistent

The indexed representation corresponds to the currently observed source
snapshot under the defined source identity.

### 6.2 out_of_sync

The source is accessible and exists, but the indexed representation does
not correspond to the current source snapshot.

### 6.3 source_missing

The authoritative source path no longer exists.

### 6.4 source_unavailable

The source identity exists or cannot be established as missing, but the
filesystem resource cannot currently be inspected because of availability
or access conditions.

---

## 7. Consistency Resolution

Consistency resolution MUST compare the authoritative source state with the
derived indexed representation.

Resolution MUST NOT:

- extract file content;
- modify the source;
- automatically re-index content;
- change permissions;
- grant access;
- invoke an LLM;
- generate embeddings;
- perform retrieval ranking.

The resolver only determines consistency state.

---

## 8. Refresh Boundary

Refreshing an out-of-sync representation is a separate orchestration
operation.

Consistency resolution MUST NOT implicitly perform extraction or indexing.

A later refresh operation MAY invoke the existing file intelligence
pipeline after authorization and capability checks.

---

## 9. Missing Source

When the authoritative source is missing, the derived indexed
representation MUST NOT be treated as current source content.

The consistency layer MUST report `source_missing`.

The consistency layer MUST NOT recreate, move, delete, or modify source data.

---

## 10. Unavailable Source

When the source cannot currently be inspected because of access or
filesystem availability conditions, the consistency layer MUST report
`source_unavailable`.

An unavailable source MUST NOT be treated as a successfully verified
current source.

---

## 11. Retrieval Boundary

Retrieval MUST NOT treat an indexed representation as current when the
consistency state indicates that it is not eligible under the retrieval
contract.

This contract does not define retrieval ranking or search semantics.

---

## 12. Permission Boundary

Consistency checking MUST respect the existing filesystem authorization
boundary.

Consistency resolution MUST NOT grant or escalate permissions.

---

## 13. Source Authority

The filesystem remains authoritative.

The indexed representation remains derived.

The index MUST NOT become the authority for determining whether the source
exists or what its current filesystem metadata is.

---

## 14. Separation of Responsibilities

This contract remains independent from:

- content extraction;
- normalization;
- content indexing implementation;
- retrieval ranking;
- embeddings;
- vector databases;
- LLM processing;
- cloud connectors;
- email connectors;
- background watcher services;
- automatic synchronization daemons.

---

## 15. Read-Only Behavior

Consistency resolution is observational.

It MUST NOT:

- modify files;
- rename files;
- move files;
- delete files;
- modify permissions;
- execute files;
- upload files;
- share files.

---

## 16. Determinism

Given the same authoritative source state and the same indexed
representation, consistency resolution should produce the same consistency
state.

---

## 17. Contract Version

Version: 1

Changes to source identity, consistency states, timestamp semantics,
content-hash semantics, authorization behavior, or refresh boundaries
require an explicit contract revision.
