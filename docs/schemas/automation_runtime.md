# Automation Runtime Integration

## Purpose

The application runtime integrates the deterministic
`AutomationScheduler` with the existing `AgentRouter`.

The scheduler remains responsible only for determining when an
automation is due and dispatching its `(route_id, request)` pair.

## Dispatch Boundary

The application runtime provides the scheduler dispatcher.

The dispatcher:

1. receives `route_id` and `request`;
2. creates a new `ConversationSession`;
3. calls `AgentRouter.run()`;
4. returns the agent result.

## Session Isolation

Each automation dispatch receives a new conversation session.

The scheduler does not own, persist, or mutate conversation sessions.

## Runtime Responsibilities

The application runtime owns:

- scheduler construction;
- router integration;
- conversation-session creation;
- dispatch wiring.

## Scheduler Responsibilities

The scheduler owns:

- automation registration;
- interval evaluation;
- enabled/disabled state;
- due dispatch.

## Exclusions

This integration does not add:

- persistence;
- background threads;
- OS scheduling;
- cron;
- notifications;
- retry policy;
- LLM-based scheduling;
- automatic automation creation;
- permission escalation.
