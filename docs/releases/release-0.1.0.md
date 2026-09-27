# Personal AI Release 0.1.0

## Release Identity

- Application: `personal-ai`
- Version: `0.1.0`
- Git revision: `9f2c9e1`
- Release type: initial local Python release
- Deployment Contract: Version 1

## Supported Runtime

- Python: `>=3.11,<3.13`
- Runtime environment: isolated Python environment

## Package

- Distribution: `personal-ai`
- Import namespace: `personal_ai`
- Entry point: `personal-ai = personal_ai.application.main:main`

## Runtime Dependencies

- `PyYAML>=6.0`

## Development Dependencies

- `pytest>=8.0`
- `ruff>=0.6`

## Required Configuration

The release expects the repository configuration boundary:

- `config/llm.yaml`
- `config/permissions/permissions.yaml`
- `config/sources/sources.yaml`
- `config/filesystem.yaml`

Default deployment behavior remains deny-by-default. The local filesystem source remains disabled unless explicitly enabled through configuration and authorized through the existing permission and filesystem-scope boundaries.

## Validation Results

Validation completed before this release record:

- `python -m compileall -q src tests` — PASS
- `python -m pytest -q` — 288 passed, 1 skipped
- `ruff check .` — PASS
- `python -m pip check` — PASS
- `personal-ai` entry point — PASS
- Deployment integration test — PASS
- Clean-environment wheel installation validation — PASS
- Release artifact content audit — PASS
- Tracked sensitive-file audit — PASS
- Tracked personal/local-path audit — PASS

## Release Artifacts

Generated distribution artifacts:

- `personal_ai-0.1.0-py3-none-any.whl`
  - SHA256: `3F74A50F633B417BC539F24B470308B99CF36820A8AFC96742879C70E0D9DB08`
- `personal_ai-0.1.0.tar.gz`
  - SHA256: `B299276A8541B48C5CFD3C6EF0B09A4BD84E3F7C2F81F3C6E06DA840E6BF3607`

The generated `dist/` artifacts are release outputs and are not committed to Git.

## Safety Boundary

This release does not grant destructive permissions, execute external actions, modify personal data, expose credentials, or expand filesystem scope.

## Reproducibility

The release is reproducible from the Git revision above, the declared project metadata, supported Python runtime, and required repository configuration.

## Release Checkpoint

Release record prepared from a clean Git working tree after deployment integration validation.

Git revision: `9f2c9e1`
