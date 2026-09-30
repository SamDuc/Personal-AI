# Personal AI 0.2.0 Release Record

## Release Identity

- Version: `0.2.0`
- Git revision: `83364e8835d5c0a124cd99f24f2d41f9a162347c`
- Previous release: `0.1.0`
- Previous release tag: `v0.1.0`
- Release type: Minor release

## Scope

This release follows the `v0.1.0` production release and includes the
LLM provider capability and execution-strategy boundaries introduced
after the `v0.1.0` tag.

Included areas:

- LLM provider registry
- Provider resolution
- Provider capability metadata and resolution
- LLM execution strategy
- Offline and online capability paths
- Application bootstrap integration
- OpenAI-compatible response-boundary hardening

## Development Dependencies

- `pytest>=8.0`
- `ruff>=0.6`

## Required Configuration

The release expects the repository configuration boundary:

- `config/llm.yaml`
- `config/permissions/permissions.yaml`
- `config/sources/sources.yaml`
- `config/filesystem.yaml`

Default deployment behavior remains deny-by-default. The local filesystem
source remains disabled unless explicitly enabled through configuration
and authorized through the existing permission and filesystem-scope
boundaries.

## Validation Results

Validation status: PENDING

The following checks must pass before release lock:

- `python -m compileall -q src tests`
- `python -m pytest -q`
- `ruff check .`
- `python -m pip check`
- `git diff --check`
- `personal-ai` entry point
- Production wheel installation
- Production installation is non-editable
- External hybrid LLM configuration
- OpenAI-compatible provider selection
- Real LLM production smoke test
- Release artifact content audit
- Artifact SHA256 verification
- Security acceptance
- Working tree clean

## Release Artifacts

Artifact generation: PENDING

- `personal_ai-0.2.0-py3-none-any.whl`
  - SHA256: PENDING
- `personal_ai-0.2.0.tar.gz`
  - SHA256: PENDING

The generated release artifacts are release outputs and are not committed
to Git.

## Safety Boundary

This release does not grant destructive permissions, execute external
actions, modify personal data, expose credentials, or expand filesystem
scope.

## Reproducibility

The release must be reproducible from the Git revision above, declared
project metadata, supported Python runtime, and required repository
configuration.

## Release Checkpoint

Release record created for source revision `83364e8835d5c0a124cd99f24f2d41f9a162347c`.
Final release checkpoint remains PENDING until deployment, security,
regression, artifact, real-LLM, and clean-environment validation pass.
