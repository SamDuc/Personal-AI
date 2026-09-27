# Automation Contract

## Purpose

The automation boundary represents a scheduled request that may later be
dispatched through the existing agent routing boundary.

Automation defines **when and what request should be triggered**.
It does not define permissions or execution capabilities.

## Contract Version

Version: `1`

Supported implementation:

`SUPPORTED_AUTOMATION_VERSION = 1`

## AutomationDefinition

An `AutomationDefinition` contains:

- `automation_id`: non-empty string identifying the automation.
- `request`: non-empty user request that will be preserved for dispatch.
- `route_id`: non-empty agent route identifier.
- `interval_seconds`: positive integer representing the minimum recurring interval.
- `enabled`: boolean indicating whether the automation is active.
- `version`: supported contract version.

The definition is immutable.

## Validation

The boundary rejects:

- empty or non-string `automation_id`;
- empty or non-string `request`;
- empty or non-string `route_id`;
- boolean or non-integer `interval_seconds`;
- non-positive `interval_seconds`;
- non-boolean `enabled`;
- unsupported contract versions.

## Architectural Boundary

Automation must not:

- construct or select an LLM provider;
- access the filesystem directly;
- access memory directly;
- construct a permission evaluator;
- grant or modify permissions;
- execute tools directly;
- perform external actions;
- modify personal data directly;
- bypass `AgentRouter`;
- bypass the existing `Agent`, `Planner`, or `Executor` boundaries.

The scheduler/dispatcher implementation is intentionally outside this contract.

## Initial Scope

Version 1 intentionally does not define:

- cron expressions;
- timezone/calendar semantics;
- persistence;
- background threads;
- operating-system schedulers;
- cloud schedulers;
- retry policy;
- notification delivery;
- external actions.

Those concerns require separate contracts before implementation.
