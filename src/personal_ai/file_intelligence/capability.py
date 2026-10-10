"""File intelligence capability resolution."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FileCapability:
    """Describe extraction capability for a file."""

    mime_type: str | None
    extension: str | None
    extraction_supported: bool
    extractor_type: str | None


_SUPPORTED_MIME_TYPES = {
    "text/plain": "text",
}

_SUPPORTED_EXTENSIONS = {
    ".txt": "text",
}


def resolve_file_capability(
    *,
    mime_type: str | None,
    extension: str | None,
) -> FileCapability:
    """Resolve the extraction capability for a file."""
    normalized_mime = mime_type.casefold() if mime_type else None
    normalized_extension = extension.casefold() if extension else None

    extractor_type = None

    if normalized_mime in _SUPPORTED_MIME_TYPES:
        extractor_type = _SUPPORTED_MIME_TYPES[normalized_mime]
    elif normalized_extension in _SUPPORTED_EXTENSIONS:
        extractor_type = _SUPPORTED_EXTENSIONS[normalized_extension]

    return FileCapability(
        mime_type=mime_type,
        extension=extension,
        extraction_supported=extractor_type is not None,
        extractor_type=extractor_type,
    )
