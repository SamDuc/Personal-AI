# Automation Scheduler Contract

## Purpose

`AutomationScheduler` provides deterministic in-memory scheduling for
`AutomationDefinition` objects.

The scheduler decides whether an automation is due and dispatches due
requests through an injected callable.

## Boundary

The scheduler:

- stores automation definitions in memory;
- evaluates recurring intervals;
- skips disabled automations;
- dispatches due `(route_id, request)` pairs;
- records the successful dispatch time.

The scheduler does not:

- construct or select an LLM provider;
- access the filesystem;
- access memory;
- construct or modify permissions;
- execute tools;
- perform external actions;
- construct or bypass `AgentRouter`;
- construct an `Agent`;
- create threads or background workers;
- use cron or operating-system schedulers;
- persist automation definitions;
- implement retry or notification policy.

## Deterministic Clock

The caller supplies `now` to `is_due()` and `run_due()`.

The scheduler does not read the system clock internally.

This keeps scheduling behavior deterministic and directly testable.

## Dispatch

The dispatcher is injected into the scheduler:

`dispatcher(route_id, request)`

The scheduler preserves both values exactly.

Router integration is intentionally deferred to a later boundary.
