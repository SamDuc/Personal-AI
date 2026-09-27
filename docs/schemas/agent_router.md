# Agent Router Contract

## 1. Purpose

The router selects an authorized specialized agent for a request.

The router is an orchestration boundary. It does not implement the
specialized agent capability itself.

## 2. Responsibilities

The router is responsible for:

- accepting a routing request;
- selecting a registered agent;
- preserving the original user request;
- returning the selected agent;
- rejecting unknown routes.

## 3. Agent Boundary

The router MUST NOT:

- construct an LLM provider;
- select an LLM provider;
- access personal data directly;
- access filesystem contents directly;
- execute tools directly;
- grant permissions;
- modify memory;
- perform external actions;
- create automation.

## 4. Route Identity

A route MUST have an explicit string identifier.

Route identifiers are configuration/application metadata and MUST NOT
implicitly grant permissions.

## 5. Specialized Agent Boundary

A specialized agent remains responsible for its own capability
orchestration while remaining behind the existing Agent contract.

The router MUST NOT bypass the selected agent boundary.

## 6. Unknown Routes

An unknown route MUST fail explicitly.

The router MUST NOT silently fall back to an unrelated specialized agent.

## 7. Request Preservation

Routing MUST NOT modify the user's request content.

## 8. Provider Independence

Routing MUST remain independent from:

- LLM provider;
- model;
- provider SDK;
- retrieval implementation;
- database;
- filesystem layout.

## 9. Permission Boundary

Routing does not authorize an operation.

Any personal-data access, tool execution, or external action remains
subject to the existing permission boundary.

## 10. Initial Scope

The initial implementation uses deterministic explicit route selection.

Semantic or LLM-based routing is outside the initial scope.

## 11. Contract Version

Contract version: 1.
