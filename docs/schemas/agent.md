# Agent Contract

## 1. Purpose

This contract defines the boundary for an agent that coordinates
authorized system capabilities to fulfill a user request.

The agent is responsible for reasoning and orchestration across
existing system capabilities while keeping retrieval, LLM execution,
permissions, tools, and automation as separate responsibilities.

The agent does not replace the existing retrieval, LLM, permission,
or tool boundaries.

## 2. Agent Responsibility

The agent is responsible for:

- accepting a user request;
- coordinating conversation context;
- determining whether available system capabilities are required;
- requesting retrieval when retrieval is explicitly available;
- requesting LLM generation through the existing LLM integration boundary;
- producing a response for the user.

The agent MUST keep capability orchestration separate from the
implementation of individual capabilities.

## 3. User Request

An agent request MUST contain the user's input as a string.

The agent MUST preserve the user's request content when passing it to
the appropriate system capability.

The agent MUST NOT modify the user's request in a way that changes its
meaning before LLM processing.

## 4. Conversation Boundary

The agent MAY operate with an existing conversation session.

When a conversation session is provided, the agent MUST use the
existing session boundary for conversation state.

The agent MUST NOT:

- modify the session's internal message collection directly;
- reorder existing messages;
- remove existing messages;
- convert conversation messages into long-term memory.

Conversation state remains governed by the existing
`ConversationSession` contract.

## 5. LLM Boundary

The agent MUST use the existing LLM integration boundary for model
generation.

The agent MUST NOT:

- construct an LLM provider;
- select an LLM provider;
- construct provider-specific requests;
- invoke `LLMProvider.generate()` directly;
- depend on a provider-specific SDK;
- depend on a provider-specific response format.

LLM execution remains governed by the existing LLM runtime and
integration contracts.

## 6. Retrieval Boundary

The agent MAY request retrieval when the user request requires
information from authorized personal data.

Retrieval remains a separate capability.

The agent MUST NOT:

- access local files directly;
- access content indexes directly;
- perform filesystem discovery directly;
- perform content extraction directly;
- implement lexical or semantic search internally;
- bypass retrieval permissions.

Retrieval remains governed by the existing retrieval contracts.

## 7. Personal Data Boundary

The agent MUST NOT assume that personal data is available merely
because the agent is executing.

Access to personal data MUST occur through authorized system
capabilities.

The agent MUST NOT:

- read arbitrary files;
- access credentials or secrets as ordinary knowledge;
- access disabled data sources;
- bypass source-specific permissions;
- scan the entire filesystem without an explicit scope.

## 8. Tool Boundary

The agent MAY coordinate tools when tools are explicitly provided by
the system.

Tools remain separate capabilities.

The agent MUST NOT:

- implement tool-specific functionality inside the agent;
- bypass tool permission checks;
- execute destructive operations without the required permission;
- treat tool availability as authorization.

Tool execution remains governed by the permission boundary.

## 9. Permission Boundary

The agent does not grant permissions.

Any action involving personal data or external side effects MUST remain
subject to the existing permission system.

The agent MUST NOT:

- grant itself permissions;
- bypass deny-by-default rules;
- perform destructive actions without authorization;
- send external messages without authorization;
- modify, move, rename, or delete data without authorization.

Permission checks remain authoritative.

## 10. External Actions

Externally visible actions remain outside the direct responsibility of
the agent.

The agent MAY request an authorized action through the appropriate
tool or action capability.

The agent MUST NOT directly:

- send email;
- share resources;
- delete files;
- move files;
- rename files;
- modify external systems.

Actions requiring confirmation remain subject to the confirmation rules
defined by the permission layer.

## 11. Memory Boundary

The agent MUST remain separate from long-term memory.

The agent MUST NOT automatically convert user requests or conversation
content into persistent memory.

The agent MUST NOT:

- create memory records;
- modify memory records;
- delete memory records;
- infer persistent user facts as a side effect of ordinary
  conversation;
- bypass the memory validation and storage boundaries.

Any promotion of information into long-term memory MUST occur through
an explicit memory-layer operation.

## 12. Agent Output

An agent operation MUST produce a response suitable for the user.

The response MUST be derived from the capabilities actually executed
by the agent.

The agent MUST NOT claim that an action was performed when the
corresponding capability did not successfully perform that action.

The agent MUST propagate relevant capability failures rather than
representing failed operations as successful.

## 13. Capability Independence

The agent MUST remain independent from:

- a specific cloud LLM provider;
- a specific local model runtime;
- a specific model;
- a specific provider SDK;
- a specific retrieval implementation;
- a specific vector store;
- a specific database;
- a specific filesystem layout;
- a specific external service.

Agent orchestration MUST remain usable when underlying capabilities
are replaced.

## 14. Safety Boundary

The agent is an orchestration layer and does not expand system
authority.

The agent MUST operate within the permissions and capabilities
available to it.

The agent MUST NOT:

- bypass permission checks;
- access secrets;
- perform unauthorized external actions;
- silently escalate privileges;
- treat model output as authorization;
- treat retrieved content as permission to act.

Model-generated instructions MUST NOT override system permissions or
safety boundaries.

## 15. Automation Boundary

The agent MUST remain separate from automation.

The agent MUST NOT:

- create recurring tasks automatically;
- schedule actions automatically;
- modify automation configuration;
- trigger future actions without the appropriate automation
  capability and authorization.

Automation remains a separate system capability.

## 16. Provider and Capability Errors

If an underlying capability fails, the agent MUST NOT represent the
operation as successful.

Capability-specific error handling remains behind the corresponding
capability boundary.

The agent MAY propagate an error or return a user-facing response
describing that the requested capability could not be completed.

The agent MUST preserve the distinction between:

- successful generation;
- unsuccessful generation;
- successful retrieval;
- unsuccessful retrieval;
- successful action;
- unsuccessful action.

## 17. Auditability

Agent operations MUST remain compatible with the system requirement
that agent actions be auditable.

The agent MUST NOT hide externally visible actions or capability
invocations from the system's audit boundary.

Audit persistence and audit storage are outside the scope of this
contract.

## 18. Separation of Responsibilities

The agent is responsible for:

- receiving user requests;
- coordinating authorized capabilities;
- coordinating conversation context;
- requesting retrieval when required;
- requesting LLM generation through the existing integration boundary;
- producing a user-facing response.

The agent does not define:

- LLM provider configuration;
- provider selection;
- provider construction;
- provider SDK integration;
- retrieval implementation;
- filesystem discovery;
- content extraction;
- memory storage;
- memory validation;
- tool implementation;
- permission policy;
- external action implementation;
- automation;
- audit persistence.

## 19. Initial Implementation Scope

The first agent implementation MUST be a minimal orchestration layer.

The initial implementation MUST:

- operate with the existing `ConversationSession`;
- use the existing LLM integration boundary;
- avoid direct personal-data access;
- avoid direct tool execution;
- avoid external actions;
- avoid automation;
- avoid automatic memory persistence.

The initial implementation exists to validate the agent boundary and
request/response orchestration before additional capabilities are
integrated.

## 20. Contract Version

Contract version: 1.