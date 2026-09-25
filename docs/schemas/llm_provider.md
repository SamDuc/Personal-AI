# LLM Provider Contract

## 1. Purpose

This contract defines the stable interface between the Personal AI
system and an LLM provider.

The provider implementation is replaceable.

The system must not depend on a single model provider.

## 2. Supported Provider Modes

The architecture supports:

- cloud LLM providers;
- local LLM providers;
- hybrid execution.

This contract does not select a specific provider.

## 3. Request

An LLM request contains an ordered collection of chat messages.

Each message contains:

- `role`;
- `content`.

The contract does not prescribe a specific provider SDK or wire protocol.

## 4. Response

An LLM response contains generated text.

Provider-specific response formats remain behind the provider interface.

## 5. Provider Interface

An LLM provider MUST expose a stable generation operation that accepts
an LLM request and returns an LLM response.

Provider-specific implementations MUST conform to this interface.

## 6. Provider Independence

The contract MUST remain independent from:

- a specific cloud provider;
- a specific local model runtime;
- a specific SDK;
- a specific model;
- a vector store;
- a retrieval implementation;
- an agent implementation.

## 7. Safety Boundary

This contract does not grant data access or action permissions.

Data access remains governed by the existing permission layer.

Externally visible or destructive actions remain subject to the
permission and confirmation rules defined elsewhere in the system.

## 8. Separation of Responsibilities

The LLM provider is responsible for model generation.

The provider contract does not define:

- retrieval;
- filesystem discovery;
- content extraction;
- indexing;
- embeddings;
- vector storage;
- agent actions;
- automation.

## 9. Contract Version

Contract version: 1.
