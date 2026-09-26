# Conversation and Session Contract

## 1. Purpose

This contract defines the boundary for managing an active
conversation session within the Personal AI system.

A conversation session represents the ordered interaction state
between a user and the system.

The session layer is responsible for conversation state.

It is not responsible for long-term memory, retrieval, model
selection, provider construction, or agent actions.

## 2. Conversation Model

A conversation consists of an ordered collection of chat messages.

Each message contains:

- `role`;
- `content`.

The message representation MUST remain compatible with the existing
`ChatMessage` model defined by the LLM provider contract.

Message order MUST be preserved.

The session MUST NOT modify message content when storing or returning
messages.

## 3. Session Identity

Each conversation session MUST have a stable, non-empty string
session identifier.

The session identifier MUST uniquely identify the conversation within
the session management boundary.

The session identifier MUST NOT contain credentials, secrets, or
personal data.

## 4. Session Operations

The session layer MUST support:

- creating a session;
- adding a message to a session;
- retrieving the ordered messages of a session.

Adding a message MUST append it to the conversation history.

Retrieving messages MUST preserve their original order.

The session layer MUST NOT invoke an LLM provider as part of these
operations.

## 5. Session State

The initial session implementation MAY keep session state in memory.

Persistence is outside the scope of this contract.

The session contract MUST NOT require:

- a specific database;
- a specific storage engine;
- a vector store;
- a cloud service;
- a filesystem layout.

Future persistence implementations MUST remain replaceable behind the
session boundary.

## 6. Separation from Memory

Conversation/session state and long-term memory are separate concepts.

The session layer MUST NOT automatically convert conversation messages
into persistent memory.

The session layer MUST NOT:

- create memory records;
- modify memory records;
- retrieve long-term memory;
- infer persistent user facts.

Any future promotion of conversation content into memory MUST occur
through an explicit memory-layer operation.

## 7. Separation from LLM Runtime

The session layer MUST remain independent from the LLM runtime.

The session layer MUST NOT:

- construct an LLM provider;
- select an LLM provider;
- invoke `LLMProvider.generate()`;
- construct provider-specific requests;
- parse provider-specific responses.

The existing LLM runtime remains responsible for executing
`LLMRequest -> LLMProvider -> LLMResponse`.

## 8. Separation from Retrieval

The session layer MUST NOT perform retrieval.

It MUST NOT:

- search local files;
- access indexes;
- perform semantic search;
- construct retrieval results;
- access personal data sources.

Retrieval remains a separate system capability.

## 9. Safety Boundary

Session management does not grant permission to access personal data
or perform external actions.

The session layer MUST NOT:

- read arbitrary personal files;
- access credentials or secrets;
- modify source data;
- delete data;
- send external messages;
- execute agent actions.

Permission checks remain governed by the existing permission layer.

## 10. Message Validation

A session MUST reject messages that do not conform to the existing
chat message representation.

At minimum:

- `role` MUST be a string;
- `content` MUST be a string.

The session layer MUST NOT impose provider-specific message roles
beyond the existing `ChatMessage` contract.

## 11. Provider Independence

The session contract MUST remain independent from:

- a specific cloud provider;
- a specific local model runtime;
- a specific SDK;
- a specific model;
- a specific API.

Conversation state MUST remain usable regardless of which supported
LLM provider is selected.

## 12. Persistence Boundary

The initial implementation does not require persistent storage.

If persistence is introduced later, the persistence mechanism MUST
remain behind a replaceable interface.

Persistence MUST NOT change the session's public conversation model.

## 13. Separation of Responsibilities

The session layer is responsible for:

- session identity;
- ordered conversation state;
- message insertion;
- message retrieval.

The session layer does not define:

- LLM provider configuration;
- provider selection;
- provider construction;
- LLM execution;
- retrieval;
- memory;
- embeddings;
- vector storage;
- agent behavior;
- tool execution;
- automation;
- external actions.

## 14. Contract Version

Contract version: 1.