from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from personal_ai.core.models import DataItem
from personal_ai.file_intelligence.index import ContentIndex
from personal_ai.filesystem.scope import FilesystemAccessScope
from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.sources.config import SourceConfig


@dataclass
class LocalCanonicalContentAccess:
    """Read indexed content after checking source and access boundaries."""

    filesystem_scope: FilesystemAccessScope
    source_config: SourceConfig
    permission_evaluator: PermissionEvaluator
    content_index: ContentIndex

    def read(self, item: DataItem) -> str | None:
        if item.source != "local_filesystem":
            return None

        if not item.content_available or not item.searchable:
            return None

        if not item.content_ref or item.sync_status != "indexed":
            return None

        if not item.content_hash:
            return None

        if not item.access_policy.read:
            return None

        if not self.source_config.is_enabled(item.source):
            return None

        if (
            self.permission_evaluator.evaluate(item.source, "read")
            != "allowed"
        ):
            return None

        source_path = Path(item.source_id).expanduser().resolve()

        if not self.filesystem_scope.is_allowed(source_path):
            return None

        return self.content_index.get_content(
            item.content_ref,
            source_path=str(source_path),
            content_hash=item.content_hash,
        )
