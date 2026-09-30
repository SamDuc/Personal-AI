# Runtime Failure Contract

## 1. Purpose

This contract defines failure behavior across the LLM runtime,
integration, agent, and routing boundaries.

The contract establishes failure propagation without introducing
provider-specific recovery behavior.

## 2. Failure Propagation

A failure raised by an LLM provider MUST propagate through:

`LLMProvider -> LLMRuntime -> LLMIntegration -> Agent -> AgentRouter`

unless an explicitly defined higher-level contract states otherwise.

The runtime and orchestration layers MUST NOT silently swallow
provider failures.

## 3. Runtime Boundary

`LLMRuntime.generate()` MUST:

- invoke the supplied `LLMProvider`;
- return the provider-produced `LLMResponse` on success;
- propagate provider generation failures to its caller;
- avoid provider-specific recovery behavior.

The runtime MUST NOT fabricate an `LLMResponse` after a provider failure.

## 4. Integration Boundary

`LLMIntegration.generate()` MUST:

- propagate runtime failures;
- append an assistant message only after successful generation;
- never create an assistant message representing a failed generation;
- preserve existing conversation messages when generation fails.

## 5. Agent Boundary

`Agent.run()` MUST:

- propagate LLM integration failures;
- preserve the submitted user request in the conversation session;
- never return a successful response when LLM generation fails;
- never fabricate an assistant response.

## 6. Router Boundary

`AgentRouter.run()` MUST:

- resolve the requested route;
- propagate agent execution failures;
- reject unknown routes explicitly;
- never convert an agent failure into a successful route result.

## 7. Recovery Scope

This contract does not define:

- retries;
- exponential backoff;
- provider fallback;
- circuit breakers;
- health checks;
- automatic provider switching.

Those mechanisms, if introduced later, MUST be defined by a separate
runtime reliability contract.

## 8. State Safety

A failed generation MUST NOT:

- append a successful assistant message;
- remove existing conversation messages;
- reorder existing conversation messages;
- fabricate a response.

## 9. Error Identity

Unless a higher-level contract explicitly transforms an error,
the original failure type and error information MUST remain observable
to the caller.

## 10. Contract Version

Contract version: 1.
