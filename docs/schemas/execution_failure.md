# Execution Failure Contract

## 1. Purpose

This contract defines failure behavior at the execution boundary.

The contract establishes explicit failure propagation from a capability
through the executor without introducing recovery behavior.

## 2. Capability Failure

When a supplied capability raises an exception during execution:

- `Executor.execute()` MUST propagate the failure to its caller;
- the original exception type MUST remain observable;
- the original exception information MUST remain observable;
- the executor MUST NOT silently swallow the failure;
- the executor MUST NOT fabricate a capability result.

## 3. Execution Order

Execution steps MUST continue to follow the order defined by the
`ExecutionPlan`.

If a capability fails:

- the failed step MUST NOT produce a result;
- the executor MUST NOT replace the failed result with a fabricated value;
- the executor MUST NOT silently skip the failed step and continue;
- the failure MUST terminate the current execution call.

## 4. Unknown Capability

An unknown capability MUST fail explicitly.

The executor MUST NOT:

- silently skip the step;
- fabricate a result;
- substitute another capability;
- convert the failure into a successful execution result.

## 5. Boundary Preservation

The execution boundary MUST preserve failure identity unless a higher-level
contract explicitly transforms the failure.

The executor MUST NOT introduce:

- retries;
- exponential backoff;
- provider fallback;
- circuit breakers;
- health checks;
- automatic capability switching.

## 6. State Safety

A failed execution MUST NOT fabricate successful results.

Previously completed capability calls, if any, MUST NOT be represented as
the complete successful execution result when a later step fails.

## 7. Contract Version

Contract version: 1.
