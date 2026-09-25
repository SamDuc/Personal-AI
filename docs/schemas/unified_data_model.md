# Unified Data Model



## Purpose



Define a canonical representation for personal data regardless of

where the original data is stored.



The unified model allows local files, cloud files, emails,

database records, and other authorized resources to be represented

through a common structure.



## Canonical Entity



The primary entity is `DataItem`.



Every indexed resource should have a stable identity and enough

metadata to locate, classify, retrieve, and audit the original data.



\## DataItem



\### Identity



\- `id`

  - Internal stable identifier.

  - Must be unique within the Personal AI system.



\- `source`

  - Identifier of the originating source.

  - Examples:

    - local_filesystem

    - google_drive

    - gmail

    - onedrive

    - cloud_database



\- `source_id`

  - Native identifier assigned by the source.



\- `uri`

  - Canonical location used to access the original resource.



\### Classification



\- `item_type`

  - General resource type.

  - Examples:

    - file

    - email

    - document

    - image

    - dataset

    - database_record



\- `mime_type`

  - MIME type when available.



\- `extension`

  - File extension when applicable.



\### Metadata



\- `name`

\- `size`

\- `created_at`

\- `modified_at`



Additional source-specific metadata may be stored separately.



\### Content



\- `content_available`

  - Indicates whether searchable content can be extracted.



\- `content_ref`

  - Reference to extracted/searchable content.

  - The original source remains authoritative.



\- `content_hash`

  - Hash of the relevant content when available.

  - Used for change detection and deduplication.



\### Organization



\- `project`

  - Associated project if known.



\- `topics`

  - List of inferred or assigned topics.



\- `tags`

  - User-defined or system-generated tags.



\### Retrieval



\- `searchable`

  - Whether the item is available to retrieval systems.



\- `embedding_ref`

  - Reference to an embedding representation when one exists.



\### Synchronization



\- `indexed_at`

  - Time when the item was indexed.



\- `source_modified_at`

  - Last known modification time at the source.



\- `sync_status`

  - Examples:

    - new

    - indexed

    - changed

    - unavailable

    - error



\### Security



\- `access_policy`

  - Permission information governing access.



\- `sensitivity`

  - Classification such as:

    - normal

    - private

    - sensitive

    - restricted



Credentials, private keys, tokens, and similar secrets must not

be treated as ordinary searchable knowledge.



\## Design Principles



1\. The original source remains authoritative.

2\. The unified model stores references and metadata rather than

   unnecessarily duplicating source data.

3\. Every item must identify its source.

4\. Source-specific metadata must not break the common model.

5\. Permissions are evaluated before access or action.

6\. The model must support both local and cloud resources.

7\. The model must remain independent of any particular database,

   vector store, LLM provider, or connector implementation.



\## Example



A local PDF might conceptually become:



```yaml

id: local-abc123

source: local_filesystem

source_id: "C:/Projects/example/paper.pdf"

uri: "file:///C:/Projects/example/paper.pdf"



item_type: file

mime_type: application/pdf

extension: ".pdf"



name: "paper.pdf"

size: 245678

created_at: "..."

modified_at: "..."



content_available: true

content_ref: "index://content/local-abc123"

content_hash: "..."



project: "example"

topics:

  - computer_vision

tags:

  - research



searchable: true

embedding_ref: null



indexed_at: "..."

source_modified_at: "..."

sync_status: indexed



access_policy:

  read: true

  write: false
sensitivity: normal
