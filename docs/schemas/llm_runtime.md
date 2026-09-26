# LLM Runtime Contract

## 1. Purpose

This contract defines the runtime boundary for executing an LLM
generation request through an already constructed LLM provider.

The runtime provides a stable orchestration layer above the
LLM provider interface.

## 2. Runtime Responsibility

The runtime is responsible for:

- accepting an `LLMRequest`;
- invoking an `LLMProvider`;
- returning the resulting `LLMResponse`.

The runtime MUST NOT construct or select the provider.

## 3. Provider Dependency

The runtime MUST depend only on the stable `LLMProvider` interface.

Provider-specific implementations remain behind the provider
interface.

## 4. Request Flow

The runtime MUST support the following flow:

`LLMRequest -> LLMProvider.generate() -> LLMResponse`

The runtime MUST pass the request to the provider without changing
the provider contract.

## 5. Response Flow

The runtime MUST return the `LLMResponse` produced by the provider.

The runtime MUST NOT require a provider-specific response format.

## 6. Separation of Responsibilities

The runtime does not define or implement:

- provider configuration;
- provider selection;
- provider construction;
- provider SDK integration;
- credential management;
- retrieval;
- embeddings;
- vector storage;
- memory;
- conversation/session state;
- agent behavior;
- tool execution;
- automation;
- personal data access;
- permission management.

## 7. Safety Boundary

The runtime does not grant data access or action permissions.

The runtime MUST NOT:

- access personal data directly;
- bypass the permission layer;
- execute filesystem actions;
- send external messages;
- perform destructive operations.

## 8. Error Boundary

Provider errors MUST NOT require provider-specific behavior in the
runtime contract.

Provider-specific error handling remains outside this contract.

## 9. Provider Independence

The runtime MUST remain independent from:

- a specific cloud provider;
- a specific local model runtime;
- a specific SDK;
- a specific model;
- a specific API.

## 10. Contract Version

Contract version: 1.
