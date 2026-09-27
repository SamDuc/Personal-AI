# Evaluation Contract

## Purpose

The evaluation boundary represents the result of deterministic checks
performed against an application operation or system invariant.

Evaluation produces evidence. It does not modify application state.

## Data Model

### EvaluationEvidence

`EvaluationEvidence` is immutable evidence supplied to an evaluation.

Fields:

- `evidence_id`: explicit evidence identifier;
- `evaluation_id`: evaluation that owns the evidence;
- `check`: check supported by the evidence;
- `passed`: whether this evidence supports the check;
- `detail`: descriptive evidence detail;
- `version`: evaluation contract version.

Evidence MUST belong to the same evaluation and MUST reference a
check present in that evaluation.

### EvaluationResult

`EvaluationResult` is the immutable aggregate produced by evaluation.

Fields:

- `evaluation_id`;
- `passed`;
- `checks`;
- `failures`;
- `evidence`;
- `version`.

Existing callers may omit `evidence`; the default is an empty tuple.

## Responsibilities

The evaluation boundary:

- accepts an explicit evaluation identifier;
- records the checks that were performed;
- records explicit failures;
- records supplied evaluation evidence;
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

Evidence is descriptive data only. It MUST NOT authorize an operation.

## Deterministic Semantics

An evaluation passes when no failure is supplied.

An evaluation fails when one or more explicit failures are supplied.

The evaluator MUST NOT infer authorization from a passing evaluation.

A passing evaluation is evidence only; it is not a permission grant.

## Contract Version

Version: `1`

Supported implementation:

`SUPPORTED_EVALUATION_VERSION = 1`