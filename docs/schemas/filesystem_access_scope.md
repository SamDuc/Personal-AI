# Personal AI Filesystem Access Scope Contract

## 1. Purpose

The filesystem access scope defines the authorized path boundary for
local filesystem operations.

It complements the permission layer without replacing it.

Permission determines whether an operation such as `local_filesystem/read`
is authorized.

Filesystem access scope determines whether the requested filesystem
resource is within the explicitly authorized path boundary.

## 2. Responsibilities

The filesystem access scope is responsible for:

- defining authorized filesystem roots;
- resolving requested filesystem paths;
- preventing access outside authorized roots;
- providing an explicit allow or deny result;
- remaining independent from file-reading implementation.

The scope MUST NOT:

- read or modify files;
- grant operation permissions;
- bypass PermissionEvaluator;
- execute tools;
- depend on LLM output;
- infer authorization from user data.

## 3. Scope Model

A filesystem scope MUST contain one or more explicitly authorized roots.

An empty scope MUST authorize no filesystem path.

Authorized roots MUST be represented as filesystem paths.

## 4. Path Evaluation

A requested path MUST be resolved before containment evaluation.

A requested path is allowed only when its resolved path is contained
within an explicitly authorized root.

Path-prefix string matching MUST NOT be used as the authorization rule.

## 5. Boundary

Filesystem scope is evaluated after operation permission and before
filesystem execution.

The intended execution flow is:

Permission Check
  -> Scope Check
  -> Tool Execution
  -> Tool Result

A denied permission MUST NOT proceed to scope evaluation for execution.

A path outside the authorized scope MUST NOT be executed even when the
operation itself is permitted.

## 6. Safety

The filesystem scope MUST preserve:

- explicit scope;
- deny-by-default behavior;
- no implicit filesystem-wide access;
- no traversal outside authorized roots;
- no authorization based on LLM output;
- no execution of paths outside the configured scope.

## 7. Symlink / Resolved Path Rule

Scope evaluation MUST use the resolved filesystem path.

The implementation MUST NOT authorize a path solely because its
unresolved textual path appears to be inside an authorized root.

## 8. Initial Scope

The first implementation provides only:

- authorized root configuration;
- path normalization/resolution;
- containment evaluation;
- explicit allow/deny result.

It does not implement:

- file reading;
- file writing;
- dynamic scope changes;
- user confirmation UI;
- connector-specific permissions;
- cloud storage scope;
- automation.

## 9. Relationship to Permission

Filesystem scope does not replace permission evaluation.

Both conditions are required:

Permission(local_filesystem, operation) == allowed

AND

requested path == within authorized filesystem scope

Only then may the protected filesystem tool execute.

## 10. Contract Version

Version: 1
