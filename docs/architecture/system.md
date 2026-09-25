# Personal AI System Architecture

## Objective

Build a local-first personal AI agent system capable of
retrieving, organizing, reasoning over, and acting on authorized
personal data.

## Data Sources

- Local filesystem
- Google Drive
- Gmail
- OneDrive
- Cloud databases
- Authorized APIs
- Browser automation when an API is unavailable or insufficient

## Architecture Principles

1. Local-first.
2. Source data remains at its original location whenever possible.
3. Local indexes contain metadata and permitted searchable representations.
4. Cloud data is accessed through official APIs/connectors whenever possible.
5. Browser automation is a fallback integration mechanism.
6. Credentials and secrets are never stored in Git.
7. Destructive or externally visible actions require explicit permission.
8. LLM providers remain replaceable.
9. Data access is scoped by source and permission policy.
10. Agent actions must be auditable.

## Core Layers

Profile
Memory
Projects
Data Intelligence
Connectors
Retrieval
LLM Provider
Agents
Tools
Permissions
Automation

## Data Flow

Source
  -> Connector
  -> Normalization
  -> Metadata
  -> Index
  -> Retrieval
  -> Agent
  -> Permission Check
  -> Response or Action

## LLM Strategy

The system must not depend on a single model provider.

Supported architecture:

- Cloud LLM providers
- Local LLM providers
- Hybrid execution

The model provider is an implementation detail behind a stable interface.

## Safety

Default permissions are deny-by-default.

The system must not:

- delete files automatically
- move files automatically
- send emails automatically
- share cloud resources automatically
- access credentials or secrets as ordinary knowledge
- scan the entire filesystem without an explicit scope

## Initial Development Strategy

Development proceeds from contracts and local indexing
toward connectors, retrieval, model integration, agents,
and finally automation.
