# Agent Capability Orchestration Boundary

## 1. Purpose

This contract defines the capability orchestration boundary between
the Agent and supplied execution capabilities.

## 2. Boundary

The Agent coordinates capabilities through the existing:

- Planner;
- ExecutionPlan;
- Executor;
- supplied Capability.

No additional capability abstraction is introduced by this contract.

## 3. Capability Ownership

Capabilities MUST be supplied to the Executor.

The Executor MUST NOT construct:

- LLM providers;
- retrievers;
- filesystem access;
- permission evaluators;
- external service clients.

## 4. Planning Separation

The Planner MUST produce an ExecutionPlan only.

The Planner MUST NOT execute capabilities.

## 5. Execution

The Executor MUST:

- accept an ExecutionPlan;
- resolve declared capabilities;
- execute steps in plan order;
- return capability results;
- reject unknown capabilities explicitly.

## 6. Failure

Capability failures MUST propagate to the caller.

The Executor MUST NOT:

- swallow failures;
- fabricate results;
- silently skip failed steps;
- substitute another capability;
- retry;
- fallback;
- automatically switch capabilities.

## 7. Agent Boundary

The Agent MUST remain an orchestration layer.

The Agent MUST NOT:

- construct provider-specific requests;
- directly access filesystem contents;
- bypass retrieval;
- bypass permissions;
- implement tool-specific functionality;
- fabricate successful capability results.

## 8. Independence

The Agent capability boundary MUST remain independent from:

- a specific LLM provider;
- a specific retrieval implementation;
- filesystem implementation;
- external service implementation.

## 9. Compatibility

Existing Agent, Planner, ExecutionPlan, Executor, and execution
failure contracts remain authoritative.

## 10. Contract Version

Version: 1
