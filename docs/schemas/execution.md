# Execution Contract

## 1. Purpose

Execution consumes an explicit execution plan and dispatches its steps
to explicitly supplied capabilities.

## 2. Responsibilities

The executor:

- accepts an ExecutionPlan;
- resolves declared capabilities;
- executes steps in plan order;
- returns capability results;
- rejects unknown capabilities.

## 3. Capability Boundary

Capabilities are supplied to the executor.

The executor MUST NOT construct:

- LLM providers;
- retrievers;
- filesystem access;
- permission evaluators;
- external service clients.

## 4. Permission Boundary

The executor MUST NOT grant or infer permissions.

Tool execution remains behind ToolExecutor and PermissionEvaluator.

## 5. Data Boundary

The executor MUST NOT directly inspect personal data or filesystem contents.

## 6. Failure

Unknown capabilities MUST fail explicitly.

The executor MUST NOT silently skip or replace an unknown capability.

## 7. Contract Version

Contract version: 1.
