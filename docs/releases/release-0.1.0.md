# Personal AI Release 0.1.0

## Release Identity

- Application: `personal-ai`
- Version: `0.1.0`
- Git revision: `79ebb70`
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

Final validation for release candidate `79ebb70`:

- `python -m compileall -q src tests` - PASS
- `python -m pytest -q` - 390 passed, 1 skipped
- `ruff check .` - PASS
- `python -m pip check` - PASS
- `git diff --check` - PASS
- `personal-ai` entry point - PASS
- Production wheel installation - PASS
- Production installation is non-editable - PASS
- External hybrid LLM configuration - PASS
- OpenAI-compatible provider selection - PASS
- Real LLM production smoke test - PASS
- Release artifact content audit - PASS
- Artifact SHA256 verification - PASS
- Security acceptance - PASS
- Working tree clean - PASS

The real LLM production smoke test successfully used the configured OpenAI-compatible provider and returned a Vietnamese response through the production-installed package.

Security acceptance confirmed that secrets are supplied through environment variables rather than committed configuration, production artifacts contain no detected secret/credential filenames, permission and filesystem security regression tests pass, and the production package remains installed non-editably from the release wheel.
## Release Artifacts

Generated distribution artifacts:

- `personal_ai-0.1.0-py3-none-any.whl`
  - SHA256: `E60A5DDDDC2AE866DD1E6A3A0B7354E8179B24E3154C236C24DCBEE8AC997159`
- `personal_ai-0.1.0.tar.gz`
  - SHA256: `0A6C85C26886908665DB9DF9D69DDEA3F79A29326E630310525630A672018077`

The generated `dist/` artifacts are release outputs and are not committed to Git.

## Safety Boundary

This release does not grant destructive permissions, execute external actions, modify personal data, expose credentials, or expand filesystem scope.

## Reproducibility

The release is reproducible from the Git revision above, the declared project metadata, supported Python runtime, and required repository configuration.

## Release Checkpoint

Release record finalized from source revision `79ebb70` after deployment, security, regression, real-LLM, and clean-environment validation.

Source revision: `79ebb70`
