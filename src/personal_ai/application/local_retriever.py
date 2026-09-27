from __future__ import annotations

from collections.abc import Callable

from personal_ai.connectors.local_file_content_extraction import (
    extract_local_file_content,
)
from personal_ai.connectors.local_file_source import discover_enabled_local_files
from personal_ai.connectors.local_filesystem import local_file_to_data_item
from personal_ai.core.models import AccessPolicy
from personal_ai.filesystem.scope import FilesystemAccessScope
from personal_ai.permissions.evaluator import PermissionEvaluator
from personal_ai.retrieval.local_integration import integrate_local_content_index
from personal_ai.retrieval.local_search import (
    LocalSearchRequest,
    SearchableContent,
    search_local_content,
)
from personal_ai.sources.config import SourceConfig


def create_local_retriever(
    *,
    filesystem_scope: FilesystemAccessScope,
    source_config: SourceConfig,
    permission_evaluator: PermissionEvaluator,
) -> Callable[[str], list[str]]:
    def retrieve(query: str) -> list[str]:
        if not filesystem_scope.authorized_roots:
            return []

        if not source_config.is_enabled("local_filesystem"):
            return []

        if (
            permission_evaluator.evaluate(
                "local_filesystem",
                "read",
            )
            != "allowed"
        ):
            return []

        searchable_contents: list[SearchableContent] = []

        for root in filesystem_scope.authorized_roots:
            metadata_items = discover_enabled_local_files(
                root,
                source_config,
            )

            for metadata in metadata_items:
                if not filesystem_scope.is_allowed(metadata.path):
                    continue

                item = local_file_to_data_item(metadata)

                item.access_policy = AccessPolicy(
                    read=True,
                    write=False,
                )

                extracted = extract_local_file_content(metadata.path)

                if not extracted.content_available:
                    continue

                integrate_local_content_index(
                    item,
                    extracted,
                )

                searchable_contents.append(
                    SearchableContent(
                        item=item,
                        text=extracted.text,
                    )
                )

        results = search_local_content(
            searchable_contents,
            LocalSearchRequest(query=query),
        )

        result_ids = {result.item.id for result in results}

        return [
            searchable.text
            for searchable in searchable_contents
            if searchable.item.id in result_ids
        ]

    return retrieve