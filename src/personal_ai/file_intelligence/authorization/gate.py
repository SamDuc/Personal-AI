from dataclasses import dataclass
from pathlib import Path

from personal_ai.file_intelligence.capability import FileCapability
from personal_ai.filesystem.scope import FilesystemAccessScope
from personal_ai.permissions.evaluator import PermissionEvaluator


@dataclass(frozen=True)
class AuthorizationDecision:
    allowed: bool
    reason: str


class AuthorizationGate:
    """Authorize a file before it reaches content extraction."""

    def __init__(
        self,
        *,
        filesystem_scope: FilesystemAccessScope,
        permission_evaluator: PermissionEvaluator,
    ) -> None:
        self._filesystem_scope = filesystem_scope
        self._permission_evaluator = permission_evaluator

    def evaluate(
        self,
        *,
        source_path: str | Path,
        capability: FileCapability,
        resource_category: str,
        operation: str = "read",
    ) -> AuthorizationDecision:
        path = Path(source_path).expanduser().resolve()

        if not self._filesystem_scope.is_allowed(path):
            return AuthorizationDecision(
                allowed=False,
                reason="filesystem_scope_denied",
            )

        permission = self._permission_evaluator.evaluate(
            resource_category,
            operation,
        )

        if permission != "allowed":
            return AuthorizationDecision(
                allowed=False,
                reason=f"permission_{permission}",
            )

        if not capability.extraction_supported:
            return AuthorizationDecision(
                allowed=False,
                reason="unsupported_capability",
            )

        return AuthorizationDecision(
            allowed=True,
            reason="authorized",
        )
