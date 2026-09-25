# LLM Provider Adapter Contract

## 1. Purpose

This contract defines the adapter boundary between provider
configuration and the stable LLM provider interface.

The adapter allows provider implementations to remain replaceable.

## 2. Adapter Boundary

The adapter layer is responsible for constructing or exposing an
implementation of the stable `LLMProvider` interface.

The adapter MUST conform to the existing provider contract.

## 3. Relationship to Provider Configuration

Provider configuration is validated before adapter construction.

The adapter MUST NOT bypass configuration validation.

The adapter MUST NOT receive or persist raw credentials or secrets
through the provider configuration contract.

## 4. Provider Interface

The adapter MUST produce an object conforming to:

`LLMProvider.generate(LLMRequest) -> LLMResponse`

The existing `LLMProvider` interface MUST remain unchanged.

## 5. Provider Selection

Provider construction is responsible for selecting the appropriate
adapter from validated provider configuration.

Provider selection MUST remain separate from:

- request generation;
- retrieval;
- personal data access;
- permissions;
- agent actions;
- automation.

## 6. Provider Independence

The adapter contract MUST remain independent from:

- a specific cloud provider;
- a specific local model runtime;
- a specific SDK;
- a specific model;
- a specific API;
- a specific vector store;
- a specific retrieval implementation.

Provider-specific implementation details belong inside the adapter.

## 7. Safety Boundary

The adapter does not grant data access or action permissions.

The adapter MUST NOT:

- access personal data directly;
- bypass the permission layer;
- execute filesystem actions;
- send external messages;
- perform agent actions;
- perform destructive operations.

## 8. Initial Implementation Scope

The first implementation MUST use a fake provider adapter.

The fake adapter exists to validate:

- provider construction;
- interface conformance;
- request flow;
- response flow;
- configuration-to-provider separation.

A real provider SDK is outside the scope of the initial adapter
implementation.

## 9. Separation of Responsibilities

The adapter contract does not define:

- provider configuration validation;
- credential management;
- retrieval;
- embeddings;
- vector storage;
- conversation/session state;
- agent behavior;
- tool execution;
- automation.

## 10. Contract Version

Contract version: 1.
