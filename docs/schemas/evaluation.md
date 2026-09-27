# Evaluation Contract

## Purpose

The evaluation boundary represents the result of deterministic checks
performed against an application operation or system invariant.

Evaluation produces evidence. It does not modify application state.

## Responsibilities

The evaluation boundary:

- accepts an explicit evaluation identifier;
- records the checks that were performed;
- records explicit failures;
- determines whether the evaluation passed;
- returns an immutable evaluation result.

## Security Boundary

Evaluation MUST NOT:

- grant permissions;
- modify permission policy;
- execute tools;
- access personal data directly;
- modify filesystem contents;
- construct LLM providers;
- select LLM providers;
- modify memory;
- create automation;
- perform external actions.

Evaluation observes supplied evidence and produces a result.

## Deterministic Semantics

An evaluation passes when no failure is supplied.

An evaluation fails when one or more explicit failures are supplied.

The evaluator MUST NOT infer authorization from a passing evaluation.

A passing evaluation is evidence only; it is not a permission grant.

## Contract Version

Version: `1`

Supported implementation:

`SUPPORTED_EVALUATION_VERSION = 1`
