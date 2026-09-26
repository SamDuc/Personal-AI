# Personal AI Tool Contract

## Purpose

The Tool layer provides explicit, auditable capabilities that can be requested by agents and executed only after the required permission decision has been obtained.

Tools remain separate from agents, permissions, connectors, retrieval, and LLM providers.

## Responsibilities

A tool is responsible for:

- exposing a defined capability
- declaring the resource category it operates on
- declaring the operation it performs
- accepting a well-defined input
- requesting or receiving the required permission decision
- executing the capability only when authorized
- returning a defined result
- reporting execution failures explicitly

A tool must not:

- grant itself permission
- bypass the permission layer
- interpret tool availability as authorization
- execute a denied operation
- execute a confirmation-required operation before confirmation
- implement agent reasoning
- implement LLM provider logic
- directly bypass connectors or retrieval boundaries
- perform unrelated capabilities outside its declared scope

## Permission Boundary

Every protected tool operation must identify:

- resource category
- operation

The permission layer is authoritative.

Possible permission decisions are:

- `allowed`
- `denied`
- `confirmation_required`

Only `allowed` authorizes immediate execution.

`denied` must not be executed.

`confirmation_required` must not be executed until the required confirmation has been obtained.

The tool does not grant or modify permissions.

## Resource Categories

The initial resource categories are:

- `local_filesystem`
- `cloud_storage`
- `email`
- `database`
- `browser`

## Operations

The initial operations are:

- `read`
- `write`
- `move`
- `rename`
- `delete`
- `send`
- `update`
- `interact`

Additional policy-level confirmation operations include:

- `share`
- `external_action`

A tool must not assume that an operation is authorized merely because the operation exists in the policy.

## Tool Identity

Each tool must have a stable identifier.

A tool should expose:

- `name`
- `description`
- `resource_category`
- `operation`

The declared resource category and operation define the permission scope of the tool.

## Input

Tool input must be explicitly defined by the tool.

Input must not implicitly grant additional permissions or expand the declared resource scope.

A tool must validate its required input before execution.

## Execution

The conceptual execution flow is:

Tool Request
  -> Permission Check
  -> Permission Decision
  -> Tool Execution
  -> Tool Result

The permission check must occur before protected execution.

Permission evaluation and tool execution are separate responsibilities.

## Result

A tool result must distinguish successful execution from failure.

A successful result must represent the actual operation performed.

A tool must not report an operation as successful when execution did not occur.

A denied or unconfirmed operation must not be represented as successfully executed.

## Errors

Tool failures must be explicit and must not be silently converted into successful results.

At minimum, the tool boundary must distinguish:

- invalid input
- permission denied
- confirmation required
- execution failure

## Agent Boundary

Agents may request tools as capabilities.

Agents must not:

- implement tool-specific execution
- bypass tool permission checks
- execute protected operations directly
- treat tool availability as authorization

Tool execution remains governed by the permission boundary.

## Auditability

Tool operations must remain compatible with the system audit boundary.

A tool must not hide:

- the requested operation
- the resource category
- the permission decision
- whether execution occurred
- execution failure

## Initial Scope

Version 1 establishes the architectural contract only.

The initial implementation does not define:

- concrete tool implementations
- tool registry
- tool discovery
- confirmation UI
- external actions
- dynamic permission management
- automation
- connector-specific tool behavior

These are separate concerns and must be introduced through their own contracts.

## Version

Contract version: 1
