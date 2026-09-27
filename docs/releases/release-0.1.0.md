# Personal AI Release 0.1.0

## Release Identity

- Application: `personal-ai`
- Version: `0.1.0`
- Git revision: `572234f`
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
- `python -m pytest -q` — 361 passed, 1 skipped
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
  - SHA256: `B29050B4353C3A7A9E736FA9DD10651BA78AE586E666A23D1A2F2E311C8383DD`
- `personal_ai-0.1.0.tar.gz`
  - SHA256: `F617EEF05CC9FFB389E33BB57D3F5C78289C3560309A81FCB9E3C01A0F337953`

The generated `dist/` artifacts are release outputs and are not committed to Git.

## Safety Boundary

This release does not grant destructive permissions, execute external actions, modify personal data, expose credentials, or expand filesystem scope.

## Reproducibility

The release is reproducible from the Git revision above, the declared project metadata, supported Python runtime, and required repository configuration.

## Release Checkpoint

Release record finalized from source revision `572234f` after deployment, security, regression, and clean-environment validation.

Source revision: `572234f`
