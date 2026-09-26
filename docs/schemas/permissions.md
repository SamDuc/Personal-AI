# Personal AI Permission Contract

## 1. Purpose

The permission layer is the authoritative boundary for access to
personal data and externally visible actions.

It evaluates whether an operation is authorized under the configured
permission policy.

The permission layer does not execute the requested operation.

## 2. Responsibilities

The permission layer is responsible for:

- evaluating permission requests;
- enforcing deny-by-default behavior;
- enforcing confirmation requirements;
- returning an explicit authorization decision;
- remaining independent from agents, tools, connectors, and LLM providers.

The permission layer MUST NOT:

- execute file operations;
- execute email operations;
- execute database operations;
- execute browser interactions;
- grant permissions dynamically;
- bypass configured restrictions.

## 3. Permission Request

A permission request represents an attempted operation against a
specific capability or resource category.

A request MUST identify:

- resource category;
- requested operation.

The permission layer MAY use additional request context when required
by the configured policy.

## 4. Permission Decision

A permission evaluation MUST produce an explicit decision.

The decision MUST distinguish at least:

- allowed;
- denied;
- confirmation_required.

A denied operation MUST NOT be treated as authorized.

An operation requiring confirmation MUST NOT be treated as authorized
until the required confirmation has been obtained.

## 5. Default Policy

Permission evaluation MUST follow deny-by-default behavior.

If a requested resource category or operation is not explicitly
authorized by the configured permission policy, the result MUST be
denied.

The permission layer MUST NOT infer authorization from:

- agent intent;
- tool availability;
- LLM output;
- previous unrelated authorization;
- user data content.

## 6. Confirmation

Operations listed by the permission policy as requiring confirmation
MUST produce a confirmation_required decision.

Confirmation is separate from authorization evaluation.

The permission layer MUST NOT assume confirmation has been granted.

## 7. Policy Source

The initial permission policy is defined by:

config/permissions/permissions.yaml

The runtime permission layer MUST treat the configured policy as
authoritative.

## 8. Resource Categories

The initial policy defines these resource categories:

- local_filesystem;
- cloud_storage;
- email;
- database;
- browser.

The permission layer MUST NOT assume additional categories are
authorized unless they are represented by the configured policy.

## 9. Operations

Operations are defined by the configured permission policy.

The initial policy includes operations such as:

- read;
- write;
- move;
- rename;
- delete;
- send;
- update;
- interact.

The runtime MUST evaluate an operation against the requested resource
category rather than treating an operation name alone as authorization.

## 10. Agent Boundary

The agent does not grant permissions.

The agent MAY request an authorization decision through the permission
layer or an authorized capability.

The agent MUST NOT:

- grant itself permissions;
- bypass deny-by-default behavior;
- interpret an unauthorized operation as authorized;
- directly perform protected external actions.

## 11. Tool Boundary

Tool availability does not imply authorization.

A tool MUST obtain the required permission decision before performing
an operation protected by the permission layer.

The permission layer MUST remain independent from tool implementation.

## 12. External Actions

Externally visible actions remain subject to permission evaluation.

Examples include:

- sending email;
- sharing resources;
- deleting data;
- moving data;
- renaming data;
- modifying external systems.

The permission layer determines whether the requested operation is
allowed, denied, or requires confirmation.

It does not execute the action.

## 13. Safety

The permission layer MUST preserve the following guarantees:

- deny-by-default;
- no implicit privilege escalation;
- no authorization based on LLM output;
- no execution of protected operations;
- explicit handling of confirmation requirements.

## 14. Errors

Invalid permission requests MUST result in an explicit error rather
than an implicit authorization.

Unknown resource categories MUST NOT be treated as allowed.

Unknown operations MUST NOT be treated as allowed.

## 15. Auditability

Permission decisions SHOULD provide sufficient structured information
for the calling layer to record an auditable decision.

The permission layer itself does not perform the requested operation.

## 16. Initial Scope

The first implementation should provide only permission evaluation
against the existing permissions.yaml policy.

It should not implement:

- tool execution;
- external actions;
- confirmation UI;
- automation;
- dynamic permission management.

The initial implementation exists to establish the permission boundary
before tools and automation are added.

## 17. Contract Version

Version: 1
