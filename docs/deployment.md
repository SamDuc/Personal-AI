# Personal AI Deployment Contract

## 1. Purpose

This document defines the deployment boundary for the Personal AI Agent System.

Deployment turns the repository source into a repeatable runtime environment in which the application can be initialized, configured, started, tested, and released.

Deployment must not replace the existing architecture boundaries for profile, memory, retrieval, LLM, agent, permissions, tools, or data sources.

## 2. Deployment Principles

The deployment process MUST be reproducible, explicit, local-first, configuration-driven, compatible with the supported Python version, independent of a specific LLM provider, compatible with deny-by-default permissions, safe by default, and testable from a clean environment.

Deployment MUST NOT silently enable data sources, grant permissions, expand filesystem scope, execute external actions, modify personal data, install undeclared runtime dependencies, or select a provider-specific LLM implementation without configuration.

## 3. Supported Runtime

The initial deployment target is a Python runtime.

Supported Python versions:

>=3.11,<3.13

The application MUST run inside an isolated project environment and MUST NOT depend on the user's global Python installation.

## 4. Package Boundary

The project is packaged through the build configuration declared in pyproject.toml.

The source root is src/.

The distribution package name is personal-ai.

The Python import namespace is personal_ai.

Runtime dependencies MUST be declared by project metadata. Development and test dependencies MUST remain separate from runtime dependencies.

## 5. Application Entry Point

The deployed application MUST have an explicit application entry point.

The entry point is responsible for runtime validation, configuration loading, boundary initialization, application initialization, and starting the selected application mode.

The entry point MUST NOT bypass the existing filesystem, retrieval, LLM, agent, permission, or tool boundaries.

## 6. Configuration

Deployment configuration MUST remain separate from application source code.

Configuration may define runtime mode, enabled data sources, permission policy, LLM provider configuration, authorized filesystem scope, and logging behavior.

Secrets and credentials MUST NOT be committed to Git and MUST NOT be stored as ordinary application knowledge.

## 7. Permission Initialization

Deployment MUST NOT grant permissions implicitly.

The permission system remains deny-by-default.

Tool execution MUST continue through the permission boundary.

Confirmation-required operations MUST NOT become automatically authorized through deployment.

## 8. Local Filesystem Scope

Deployment MUST NOT authorize the entire filesystem by default.

Local filesystem access MUST use an explicitly authorized scope.

A disabled local filesystem source MUST remain disabled.

A missing or invalid scope MUST NOT be replaced with a broader inferred scope.

Filesystem operations MUST remain subject to the existing source and permission boundaries.

## 9. LLM Provider Boundary

Deployment MUST NOT hard-code a specific LLM provider.

Provider selection MUST remain configuration-driven and MUST use the existing LLM provider interface and factory boundary.

Provider credentials MUST NOT be embedded in source code, tests, deployment documentation, or release artifacts.

## 10. Installation

A clean installation MUST use the supported Python version, create an isolated environment, install the project package from repository metadata, install development dependencies only when required, load configuration, validate the runtime, and execute a smoke test before normal use.

## 11. Deployment Validation

Deployment validation MUST cover package installation, Python runtime compatibility, configuration loading, permission initialization, application startup, and at least one safe application operation.

The existing automated test suite remains a prerequisite for release.

## 12. Release Artifact

A release MUST identify the Git revision, application version, supported Python version, declared dependencies, required configuration, and validation results.

Release artifacts MUST NOT contain credentials, secrets, personal data, filesystem contents, caches, or local environment state.

## 13. Development and Release Separation

Development tooling, caches, test artifacts, and temporary files MUST NOT be treated as release runtime requirements.

The release environment MUST be reproducible from repository source and declared metadata.

## 14. Deployment Modes

The initial deployment contract defines three modes: local development, clean-environment validation, and release.

Future deployment targets such as Windows executables, Windows services, Docker, Linux services, or Raspberry Pi services are outside the initial deployment contract.

## 15. Safety Boundary

Deployment MUST NOT grant destructive permissions, perform destructive filesystem operations, execute external actions, modify personal data, expose secrets, or expand authorized filesystem scope.

## 16. Deployment Test Flow

The deployment validation flow is:

1. Install the package in an isolated environment.
2. Validate the supported Python runtime.
3. Load and validate configuration.
4. Initialize the permission boundary.
5. Initialize the application boundary.
6. Start the application.
7. Execute a safe operation.
8. Verify the result.

## 17. Initial Scope Exclusions

The initial deployment phase does not include a CLI framework, GUI, web server, Docker image, Windows service, systemd service, executable packaging, cloud deployment, automatic updates, or remote administration.

## 18. Deployment Sequence

The deployment implementation sequence is:

1. Deployment Contract
2. Runtime / Environment Contract
3. Configuration Contract
4. Application Entry Point
5. Bootstrap / Initialization
6. Installation Procedure
7. Smoke Test
8. Deployment Integration Test
9. Release Artifact
10. Clean Environment Validation
11. Release Checkpoint

## 19. Contract Version

Deployment Contract Version: 1
