# LLM Provider Configuration Contract

## 1. Purpose

This contract defines the configuration boundary for LLM providers.

Provider configuration describes how an LLM provider is selected and
enabled without coupling the system to a specific provider SDK,
model runtime, or model.

The provider implementation remains replaceable behind the stable
LLM provider interface.

## 2. Supported Provider Modes

The configuration must support the provider modes defined by the
system architecture:

- cloud LLM providers;
- local LLM providers;
- hybrid execution.

The configuration does not select or require a specific provider.

## 3. Configuration Structure

The configuration is represented as a versioned provider map.

The top-level structure contains:

- `version`;
- `providers`.

Each provider entry is identified by a stable provider identifier.

Example structure:

```yaml
version: 1

providers:
  <provider_id>:
    enabled: false
    type: cloud
```

## 4. Provider Configuration

Each provider configuration MUST contain:

- `enabled`;
- `type`.

`enabled` indicates whether the provider is available for use by the
LLM runtime.

`type` identifies the provider execution mode.

Supported values are:

- `cloud`;
- `local`.

## 5. Provider Independence

Provider configuration MUST remain independent from:

- a specific cloud provider;
- a specific local model runtime;
- a specific SDK;
- a specific model;
- retrieval;
- embeddings;
- vector storage;
- agent behavior;
- tool execution.

Provider-specific implementation details belong behind the provider
interface.

## 6. Credential Boundary

Credentials and secrets MUST NOT be stored directly in the provider
configuration file.

The architecture requires credentials and secrets to remain outside
Git-tracked configuration.

This contract does not define a credential storage or
secret-management system.

## 7. Validation Rules

The configuration validator MUST verify:

- `version` is present and supported;
- `providers` is present;
- each provider has a stable identifier;
- `enabled` is a boolean;
- `type` is one of the supported provider types.

The configuration MUST reject:
- missing required fields;
- invalid provider types;
- non-boolean `enabled` values;
- provider configuration that contains raw credentials or secrets.

The configuration validator MUST NOT:

- initialize a provider;
- call a provider SDK;
- generate an LLM response;
- access personal data;
- grant data permissions;
- execute agent actions;
- persist provider runtime state.

## 8. Safety Boundary

Provider configuration does not grant data access or action permissions.

Data access remains governed by the existing permission layer.

Externally visible or destructive actions remain subject to the
permission and confirmation rules defined elsewhere in the system.

Enabling an LLM provider does not grant access to personal data.

## 9. Separation of Responsibilities

Provider configuration is responsible for describing provider
availability and execution mode.

The configuration contract does not define:

- provider SDK integration;
- model invocation;
- request construction;
- response parsing;
- retrieval;
- content indexing;
- embeddings;
- vector storage;
- conversation or session state;
- agent actions;
- automation.

## 10. Contract Version

Contract version: 1.
