# Planning Contract

## 1. Purpose

Planning converts a user request into a structured execution plan.

## 2. Responsibilities

The planner:

- accepts a user request;
- validates the request boundary;
- creates an ordered execution plan;
- preserves the original request.

## 3. Prohibited Responsibilities

The planner MUST NOT:

- execute capabilities;
- access filesystem contents;
- access personal data directly;
- construct an LLM provider;
- select an LLM provider;
- bypass retrieval;
- bypass tools;
- grant permissions;
- modify memory;
- perform external actions.

## 4. Deterministic Initial Scope

The initial planner implementation is deterministic.

LLM-based planning is outside the initial scope.

## 5. Plan Contract

A plan contains:

- plan identifier;
- original request;
- ordered steps;
- plan version.

Each step contains:

- step identifier;
- capability identifier;
- input data.

## 6. Contract Version

Contract version: 1.
