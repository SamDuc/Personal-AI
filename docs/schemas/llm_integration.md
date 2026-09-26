# LLM Integration Contract

## 1. Purpose

This contract defines the integration boundary between the
conversation session layer and the LLM runtime.

The integration layer coordinates conversation state with LLM
generation while keeping session management and LLM execution as
separate responsibilities.

The integration layer does not replace the existing session or
runtime contracts.

## 2. Integration Responsibility

The integration layer is responsible for:

- accepting a conversation session;
- constructing an `LLMRequest` from the session's ordered messages;
- invoking the existing `LLMRuntime`;
- receiving the resulting `LLMResponse`;
- adding the generated assistant response to the conversation session.

The integration layer MUST preserve the existing boundaries between
session management and LLM execution.

## 3. Request Construction

The integration layer MUST construct an `LLMRequest` from the ordered
messages stored in the conversation session.

The messages in the generated `LLMRequest` MUST preserve the original
conversation order.

The integration layer MUST NOT modify message roles or message
content when constructing the request.

The integration layer MUST use the existing `ChatMessage` model.

## 4. Runtime Dependency

The integration layer MUST depend on the existing `LLMRuntime`
interface.

The integration layer MUST NOT:

- construct an LLM provider;
- select an LLM provider;
- bypass `LLMRuntime`;
- invoke `LLMProvider.generate()` directly;
- depend on a provider-specific SDK;
- depend on a provider-specific response format.

The existing runtime remains responsible for:

`LLMRequest -> LLMProvider -> LLMResponse`

## 5. Response Handling

After the runtime returns an `LLMResponse`, the integration layer
MUST convert the generated response text into an assistant
`ChatMessage`.

The assistant message MUST use:

- `role = "assistant"`;
- the response text as `content`.

The generated assistant message MUST be appended to the conversation
session after successful LLM generation.

The integration layer MUST NOT modify the generated response text.

## 6. Conversation State

A successful integration operation MUST leave the conversation
session containing:

1. the messages that existed before generation;
2. the newly generated assistant message.

The original message order MUST be preserved.

If LLM generation fails, the integration layer MUST NOT append an
assistant message representing the failed generation.

## 7. Session Boundary

The integration layer MAY read conversation messages through the
existing session interface.

The integration layer MUST use the session's message insertion
operation when adding the generated assistant response.

The integration layer MUST NOT:

- modify the session's internal message collection directly;
- replace existing messages;
- remove messages;
- reorder messages;
- convert messages into long-term memory.

## 8. Memory Separation

LLM integration MUST remain separate from long-term memory.

The integration layer MUST NOT:

- create memory records;
- modify memory records;
- retrieve long-term memory;
- infer persistent user facts.

Conversation messages remain session state unless an explicit
memory-layer operation promotes information into persistent memory.

## 9. Retrieval Separation

The integration layer MUST NOT perform retrieval.

It MUST NOT:

- search local files;
- access content indexes;
- perform semantic search;
- construct retrieval results;
- access personal data sources.

Retrieval integration remains outside the scope of this contract.

## 10. Permission and Safety Boundary

LLM integration does not grant permission to access personal data or
perform external actions.

The integration layer MUST NOT:

- read arbitrary personal files;
- access credentials or secrets;
- modify source data;
- delete data;
- send external messages;
- execute agent actions.

Existing permission controls remain authoritative.

## 11. Error Boundary

If the LLM runtime raises an error, the integration layer MUST
propagate the error to its caller.

The integration layer MUST NOT create a successful assistant message
from a failed generation.

Provider-specific error handling MUST remain behind the existing
provider and runtime boundaries.

## 12. Provider Independence

The integration layer MUST remain independent from:

- a specific cloud provider;
- a specific local model runtime;
- a specific SDK;
- a specific model;
- a specific API.

The same integration interface MUST remain usable when the underlying
LLM provider changes.

## 13. Persistence

The integration layer MUST NOT require persistent session storage.

Session persistence remains governed by the conversation/session
boundary.

The integration layer MUST work with the existing in-memory session
implementation.

## 14. Separation of Responsibilities

The integration layer is responsible for:

- converting session state into an LLM request;
- invoking the LLM runtime;
- converting the LLM response into an assistant message;
- updating the conversation session after successful generation.

The integration layer does not define:

- provider configuration;
- provider selection;
- provider construction;
- provider SDK integration;
- retrieval;
- memory;
- embeddings;
- vector storage;
- agent behavior;
- tool execution;
- automation;
- external actions.

## 15. Contract Version

Contract version: 1.